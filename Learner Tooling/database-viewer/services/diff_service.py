"""Collection diff service.

Compares two ChromaDB collections to identify added, removed,
and modified chunks between versions of a codebase.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

import chromadb
from sklearn.metrics.pairwise import cosine_similarity

from services.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


@dataclass
class ChunkDiff:
    """Represents a single chunk that differs between two collections."""
    chunk_id: str
    symbol: Optional[str]
    path: str
    change_type: str  # "added", "removed", or "modified"
    similarity: Optional[float] = None

    def to_dict(self) -> Dict:
        result = {
            "id": self.chunk_id,
            "symbol": self.symbol,
            "path": self.path,
            "change_type": self.change_type,
        }
        if self.similarity is not None:
            result["similarity"] = round(self.similarity, 6)
        return result


@dataclass
class DiffReport:
    """Summary report comparing two collections."""
    source_name: str
    target_name: str
    source_count: int = 0
    target_count: int = 0
    added: List[ChunkDiff] = field(default_factory=list)
    removed: List[ChunkDiff] = field(default_factory=list)
    modified: List[ChunkDiff] = field(default_factory=list)
    unchanged_count: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def to_dict(self) -> Dict:
        return {
            "source": self.source_name,
            "target": self.target_name,
            "source_count": self.source_count,
            "target_count": self.target_count,
            "summary": {
                "added": len(self.added),
                "removed": len(self.removed),
                "modified": len(self.modified),
                "unchanged": self.unchanged_count,
                "total_changes": self.total_changes,
            },
            "added": [d.to_dict() for d in self.added[:50]],
            "removed": [d.to_dict() for d in self.removed[:50]],
            "modified": [d.to_dict() for d in self.modified[:50]],
        }


class SymbolMatcher:
    """Matches chunks between collections by symbol name and path.

    When chunk IDs differ between collections (e.g., after re-indexing),
    this matcher uses (symbol, path) pairs to align chunks and detect
    modifications via embedding cosine similarity.
    """

    SIMILARITY_THRESHOLD = 0.98

    def find_modified(self, source_data: Dict, target_data: Dict,
                      source_col: chromadb.Collection,
                      target_col: chromadb.Collection) -> List[ChunkDiff]:
        """Find chunks that exist in both collections but have been modified."""
        source_symbols = self._build_symbol_index(source_data)
        target_symbols = self._build_symbol_index(target_data)

        common_keys = set(source_symbols.keys()) & set(target_symbols.keys())
        modified = []

        for key in common_keys:
            src_id = source_symbols[key]["id"]
            tgt_id = target_symbols[key]["id"]

            if src_id == tgt_id:
                continue

            src_emb = source_col.get(ids=[src_id], include=["embeddings"])
            tgt_emb = target_col.get(ids=[tgt_id], include=["embeddings"])

            if not src_emb["embeddings"] or not tgt_emb["embeddings"]:
                continue

            sim = cosine_similarity(
                [src_emb["embeddings"][0]],
                [tgt_emb["embeddings"][0]],
            )[0][0]

            if sim < self.SIMILARITY_THRESHOLD:
                symbol, path = key
                modified.append(ChunkDiff(
                    chunk_id=tgt_id,
                    symbol=symbol,
                    path=path,
                    change_type="modified",
                    similarity=float(sim),
                ))

        return modified

    @staticmethod
    def _build_symbol_index(data: Dict) -> Dict[tuple, Dict]:
        """Index chunks by (symbol, path) for alignment."""
        index = {}
        for i in range(len(data["ids"])):
            meta = data["metadatas"][i]
            symbol = meta.get("symbol")
            path = meta.get("path", "")
            if symbol:
                key = (symbol, path)
                index[key] = {"id": data["ids"][i], "meta": meta}
        return index


class DiffService:
    """Compares two ChromaDB collections and produces a diff report."""

    def __init__(self):
        self._manager = get_chroma_client()
        self._matcher = SymbolMatcher()

    def compare(self, source_name: str, target_name: str,
                include_modified: bool = True) -> DiffReport:
        """Compare two collections and return a diff report.

        Args:
            source_name: The "before" collection.
            target_name: The "after" collection.
            include_modified: Whether to check for modified chunks
                via embedding similarity (slower but more detailed).

        Returns:
            DiffReport with added, removed, and modified chunks.
        """
        logger.info(f"Comparing collections: '{source_name}' -> '{target_name}'")

        source_col = self._manager.get_existing_collection(source_name)
        target_col = self._manager.get_existing_collection(target_name)

        if source_col is None:
            raise ValueError(f"Source collection not found: {source_name}")
        if target_col is None:
            raise ValueError(f"Target collection not found: {target_name}")

        source_data = source_col.get(include=["metadatas"])
        target_data = target_col.get(include=["metadatas"])

        source_ids = set(source_data["ids"])
        target_ids = set(target_data["ids"])

        report = DiffReport(
            source_name=source_name,
            target_name=target_name,
            source_count=len(source_ids),
            target_count=len(target_ids),
        )

        # Chunks only in target = added
        added_ids = target_ids - source_ids
        report.added = self._build_diffs(target_data, added_ids, "added")

        # Chunks only in source = removed
        removed_ids = source_ids - target_ids
        report.removed = self._build_diffs(source_data, removed_ids, "removed")

        # Unchanged by ID
        common_ids = source_ids & target_ids
        report.unchanged_count = len(common_ids)

        # Optionally detect modified chunks via symbol matching
        if include_modified:
            report.modified = self._matcher.find_modified(
                source_data, target_data, source_col, target_col
            )

        logger.info(
            f"Diff complete: +{len(report.added)} -{len(report.removed)} "
            f"~{len(report.modified)} ={report.unchanged_count}"
        )

        return report

    @staticmethod
    def _build_diffs(data: Dict, target_ids: Set[str],
                     change_type: str) -> List[ChunkDiff]:
        """Build ChunkDiff objects for a set of IDs from collection data."""
        diffs = []
        for i in range(len(data["ids"])):
            if data["ids"][i] in target_ids:
                meta = data["metadatas"][i]
                diffs.append(ChunkDiff(
                    chunk_id=data["ids"][i],
                    symbol=meta.get("symbol"),
                    path=meta.get("path", "unknown"),
                    change_type=change_type,
                ))
        return diffs
