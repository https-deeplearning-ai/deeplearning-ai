"""Code ingestion pipeline: parse, chunk, and store Python files in ChromaDB."""

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Set

import tiktoken

logger = logging.getLogger(__name__)
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

from models.chunk import Chunk, ChunkMetadata, ChunkType
from services.chroma_client import get_chroma_client
from config import get_config


@dataclass
class IngestionProgress:
    """Tracks progress of an ingestion operation."""
    total_files: int = 0
    processed_files: int = 0
    total_chunks: int = 0
    failed_files: List[str] = field(default_factory=list)
    current_file: str = ""
    is_complete: bool = False

    @property
    def progress_percentage(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def success_count(self) -> int:
        return self.processed_files - len(self.failed_files)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "total_chunks": self.total_chunks,
            "failed_files": self.failed_files,
            "progress_percentage": round(self.progress_percentage, 1),
            "is_complete": self.is_complete,
        }


class TokenCounter:
    """Wraps tiktoken for consistent token counting."""

    def __init__(self, model_name: str = "text-embedding-3-small",
                 fallback_encoding: str = "cl100k_base"):
        try:
            self._encoder = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self._encoder = tiktoken.get_encoding(fallback_encoding)

    def count(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._encoder.encode(text))

    @property
    def encoder(self) -> tiktoken.Encoding:
        return self._encoder


class ASTParser:
    """Parses Python source code into AST nodes using tree-sitter."""

    WANTED_TYPES: Set[str] = {"function_definition", "class_definition"}

    def __init__(self):
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)

    def parse(self, source_bytes: bytes) -> Node:
        """Parse source bytes into an AST root node."""
        tree = self._parser.parse(source_bytes)
        return tree.root_node

    def collect_target_nodes(self, node: Node,
                             parents: Optional[list] = None) -> List[dict]:
        """Recursively collect function/class definition nodes (atomic).

        When a target node is found, it is collected and its children
        are NOT explored (treating the node as an atomic unit).
        """
        if parents is None:
            parents = []
        results = []
        if node.type in self.WANTED_TYPES:
            results.append({"node": node, "parents": list(parents)})
        else:
            new_parents = parents + [node]
            for child in node.children:
                results.extend(self.collect_target_nodes(child, new_parents))
        return results

    @staticmethod
    def extract_symbol_name(node: Node, source_bytes: bytes) -> Optional[str]:
        """Extract the identifier (symbol name) from a definition node."""
        for child in node.children:
            if child.type == "identifier":
                return source_bytes[child.start_byte:child.end_byte].decode("utf-8")
        return None


class TextSplitter:
    """Splits text into chunks that respect a maximum token limit."""

    def __init__(self, token_counter: TokenCounter):
        self._counter = token_counter

    def split(self, source: str, start_line: int,
              max_tokens: int) -> List[dict]:
        """Split text into token-bounded chunks.

        Uses a line-accumulator approach: lines are added to a buffer
        until the next line would exceed max_tokens, at which point
        the buffer is flushed as a chunk.
        """
        if not source.strip():
            return []
        lines = source.split("\n")
        newline_tokens = self._counter.count("\n")
        current_lines: List[str] = []
        current_tokens = 0
        split_start = start_line
        splits: List[dict] = []

        def flush():
            if not current_lines:
                return
            splits.append({
                "id": str(uuid.uuid4()),
                "document": "\n".join(current_lines),
                "start_line": split_start,
                "end_line": split_start + len(current_lines) - 1,
            })

        for line in lines:
            line_tokens = self._counter.count(line) + newline_tokens
            if current_tokens + line_tokens > max_tokens and current_lines:
                flush()
                split_start += len(current_lines)
                current_lines = []
                current_tokens = 0
            current_lines.append(line)
            current_tokens += line_tokens

        if current_lines:
            flush()

        return splits


class IngestionService:
    """Orchestrates the full pipeline: walk repo -> parse -> chunk -> store."""

    def __init__(self):
        config = get_config().ingestion
        self._ast_parser = ASTParser()
        self._token_counter = TokenCounter(
            model_name=config.tokenizer_model,
            fallback_encoding=config.fallback_encoding,
        )
        self._splitter = TextSplitter(self._token_counter)
        self._config = config
        self._chroma = get_chroma_client()

    def chunk_file(self, file_path: str,
                   max_tokens: Optional[int] = None) -> List[Chunk]:
        """Chunk a single Python file using hybrid AST + token splitting."""
        max_tok = max_tokens or self._config.max_tokens_per_chunk

        with open(file_path, "rb") as f:
            source_bytes = f.read()

        root = self._ast_parser.parse(source_bytes)
        nodes = self._ast_parser.collect_target_nodes(root)
        nodes.sort(key=lambda x: x["node"].start_byte)

        chunks: List[Chunk] = []
        cursor = 0
        now_str = datetime.now().isoformat()

        for item in nodes:
            node = item["node"]

            # Handle gap before this node
            if cursor < node.start_byte:
                gap_text = source_bytes[cursor:node.start_byte].decode("utf-8")
                gap_splits = self._splitter.split(
                    gap_text, node.start_point[0], max_tok
                )
                for s in gap_splits:
                    chunks.append(Chunk(
                        id=s["id"],
                        document=s["document"],
                        metadata=ChunkMetadata(
                            path=file_path,
                            start_line=s["start_line"],
                            end_line=s["end_line"],
                            symbol=None,
                            chunk_type=ChunkType.GAP.value,
                            ingested_at=now_str,
                        ),
                    ))

            # Handle the node itself
            node_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8")
            symbol = self._ast_parser.extract_symbol_name(node, source_bytes)
            node_splits = self._splitter.split(
                node_text, node.start_point[0], max_tok
            )
            for s in node_splits:
                chunks.append(Chunk(
                    id=s["id"],
                    document=s["document"],
                    metadata=ChunkMetadata(
                        path=file_path,
                        start_line=s["start_line"],
                        end_line=s["end_line"],
                        symbol=symbol,
                        chunk_type=node.type,
                        ingested_at=now_str,
                    ),
                ))

            cursor = node.end_byte

        # Trailing code after the last node
        if cursor < len(source_bytes):
            remaining = source_bytes[cursor:].decode("utf-8")
            last_line = nodes[-1]["node"].end_point[0] if nodes else 0
            tail_splits = self._splitter.split(remaining, last_line, max_tok)
            for s in tail_splits:
                chunks.append(Chunk(
                    id=s["id"],
                    document=s["document"],
                    metadata=ChunkMetadata(
                        path=file_path,
                        start_line=s["start_line"],
                        end_line=s["end_line"],
                        symbol=None,
                        chunk_type=ChunkType.GAP.value,
                        ingested_at=now_str,
                    ),
                ))

        return chunks

    def ingest_directory(self, directory: str, collection_name: str,
                         progress_callback: Optional[Callable] = None) -> IngestionProgress:
        """Ingest all Python files from a directory into a ChromaDB collection."""
        logger.info(f"Starting ingestion: directory='{directory}' collection='{collection_name}'")
        collection = self._chroma.get_collection(collection_name)
        progress = IngestionProgress()

        py_files = self._discover_python_files(directory)
        progress.total_files = len(py_files)
        logger.info(f"Discovered {len(py_files)} Python files to process")

        buffer: List[Chunk] = []
        batch_size = self._config.batch_size

        for file_path in py_files:
            progress.current_file = str(file_path)
            progress.processed_files += 1

            try:
                new_chunks = self.chunk_file(str(file_path))
                buffer.extend(new_chunks)
                progress.total_chunks += len(new_chunks)

                while len(buffer) >= batch_size:
                    batch = buffer[:batch_size]
                    buffer = buffer[batch_size:]
                    self._upload_batch(collection, batch)

            except Exception as e:
                progress.failed_files.append(f"{file_path}: {e}")

            if progress_callback:
                progress_callback(progress)

        # Final flush
        if buffer:
            self._upload_batch(collection, buffer)

        progress.is_complete = True
        if progress_callback:
            progress_callback(progress)

        logger.info(
            f"Ingestion complete: {progress.total_chunks} chunks from "
            f"{progress.success_count}/{progress.total_files} files"
        )

        return progress

    def _discover_python_files(self, directory: str) -> List[Path]:
        """Walk a directory and find all Python files, respecting ignore patterns."""
        root = Path(directory)
        ignore = set(self._config.ignore_patterns)
        files = []

        for current_root, dirs, filenames in os.walk(root):
            dirs[:] = [d for d in dirs if d not in ignore and not d.startswith(".")]
            for fname in filenames:
                if fname.startswith("."):
                    continue
                p = Path(current_root) / fname
                if p.suffix in self._config.supported_extensions:
                    files.append(p)

        return sorted(files)

    @staticmethod
    def _upload_batch(collection, chunks: List[Chunk]) -> None:
        """Upload a batch of Chunk objects to ChromaDB."""
        if not chunks:
            return
        ids = [c.id for c in chunks]
        documents = [c.document for c in chunks]
        metadatas = [c.metadata.to_dict() for c in chunks]
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
