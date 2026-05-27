"""Chunk models representing units of vectorized code."""

import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any


class ChunkType(Enum):
    """Classification of code chunk types from AST parsing."""
    FUNCTION = "function_definition"
    CLASS = "class_definition"
    MODULE = "module"
    GAP = "gap"
    UNKNOWN = "unknown"

    @classmethod
    def from_node_type(cls, node_type: str) -> "ChunkType":
        """Map a tree-sitter node type string to a ChunkType enum."""
        mapping = {
            "function_definition": cls.FUNCTION,
            "class_definition": cls.CLASS,
            "module": cls.MODULE,
        }
        return mapping.get(node_type, cls.UNKNOWN)

    @property
    def display_label(self) -> str:
        """Human-readable label for UI display."""
        labels = {
            "function_definition": "Function",
            "class_definition": "Class",
            "module": "Module",
            "gap": "Top-Level Code",
            "unknown": "Unknown",
        }
        return labels.get(self.value, "Unknown")

    @property
    def icon(self) -> str:
        """Bootstrap icon class for this chunk type."""
        icons = {
            "function_definition": "bi-braces",
            "class_definition": "bi-diagram-3",
            "module": "bi-file-earmark-code",
            "gap": "bi-code-square",
            "unknown": "bi-question-circle",
        }
        return icons.get(self.value, "bi-question-circle")


@dataclass
class ChunkMetadata:
    """Metadata attached to a code chunk for filtering and display."""
    path: str
    start_line: int
    end_line: int
    symbol: Optional[str] = None
    chunk_type: str = "unknown"
    language: str = "python"
    file_size: Optional[int] = None
    ingested_at: Optional[str] = None

    @property
    def line_range(self) -> str:
        """Format line range for display (e.g., 'L10-L25')."""
        return f"L{self.start_line}-L{self.end_line}"

    @property
    def line_count(self) -> int:
        """Number of lines spanned by this chunk."""
        return self.end_line - self.start_line + 1

    @property
    def filename(self) -> str:
        """Extract just the filename from the full path."""
        return self.path.split("/")[-1] if "/" in self.path else self.path

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, filtering out None values (for ChromaDB)."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkMetadata":
        """Reconstruct from a ChromaDB metadata dictionary."""
        return cls(
            path=data.get("path", "unknown"),
            start_line=data.get("start_line", 0),
            end_line=data.get("end_line", 0),
            symbol=data.get("symbol"),
            chunk_type=data.get("chunk_type", "unknown"),
            language=data.get("language", "python"),
            file_size=data.get("file_size"),
            ingested_at=data.get("ingested_at"),
        )


@dataclass
class Chunk:
    """A single chunk of code ready for storage in ChromaDB."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document: str = ""
    metadata: ChunkMetadata = field(default_factory=lambda: ChunkMetadata(
        path="unknown", start_line=0, end_line=0
    ))

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (chars / 4)."""
        return len(self.document) // 4

    @property
    def is_empty(self) -> bool:
        """Check if chunk has meaningful content."""
        return not self.document.strip()

    def preview(self, max_lines: int = 5) -> str:
        """Get a short preview of the chunk content."""
        lines = self.document.strip().splitlines()
        if len(lines) <= max_lines:
            return self.document.strip()
        return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"

    def to_chroma_format(self) -> Dict[str, Any]:
        """Prepare chunk for ChromaDB insertion."""
        return {
            "id": self.id,
            "document": self.document,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_chroma_result(cls, id: str, document: str,
                           metadata: Dict[str, Any]) -> "Chunk":
        """Reconstruct a Chunk from ChromaDB query results."""
        return cls(
            id=id,
            document=document,
            metadata=ChunkMetadata.from_dict(metadata),
        )
