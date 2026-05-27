"""Search result models for presenting ChromaDB query results."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable

from models.chunk import Chunk, ChunkMetadata, ChunkType


class SortOrder(Enum):
    """Sort orders for search results."""
    RELEVANCE = "relevance"
    PATH = "path"
    LINE_NUMBER = "line_number"
    SYMBOL = "symbol"


@dataclass
class SearchResult:
    """A single search result with similarity score and chunk data."""
    chunk: Chunk
    score: float
    rank: int = 0
    highlights: List[str] = field(default_factory=list)

    @property
    def score_percentage(self) -> float:
        """Convert distance score to a 0-100 similarity percentage.

        ChromaDB returns L2 distances where lower = more similar.
        We invert this for display: 100% = perfect match.
        """
        return max(0.0, min(100.0, (1.0 - self.score) * 100))

    @property
    def score_badge_class(self) -> str:
        """Bootstrap badge color class based on score quality."""
        pct = self.score_percentage
        if pct >= 80:
            return "bg-success"
        elif pct >= 60:
            return "bg-info"
        elif pct >= 40:
            return "bg-warning"
        return "bg-secondary"

    @property
    def symbol_display(self) -> str:
        """Display-friendly symbol name."""
        sym = self.chunk.metadata.symbol
        return sym if sym else "Top-Level Code"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON API responses."""
        return {
            "id": self.chunk.id,
            "code": self.chunk.document,
            "score": round(self.score, 4),
            "score_percentage": round(self.score_percentage, 1),
            "symbol": self.chunk.metadata.symbol,
            "path": self.chunk.metadata.path,
            "lines": self.chunk.metadata.line_range,
            "chunk_type": self.chunk.metadata.chunk_type,
            "rank": self.rank,
            "highlights": self.highlights,
        }


class ResultFormatter(ABC):
    """Abstract base class for result formatting strategies."""

    @abstractmethod
    def format_score(self, score: float) -> str:
        """Format a similarity score for display."""
        ...

    @abstractmethod
    def format_header(self, result: SearchResult) -> str:
        """Format the result header line."""
        ...


class DetailedFormatter(ResultFormatter):
    """Verbose formatter showing full path and score details."""

    def format_score(self, score: float) -> str:
        pct = max(0.0, min(100.0, (1.0 - score) * 100))
        return f"{pct:.1f}% match (distance: {score:.4f})"

    def format_header(self, result: SearchResult) -> str:
        meta = result.chunk.metadata
        return (
            f"[{self.format_score(result.score)}] "
            f"{meta.path}:{meta.line_range} "
            f"({result.symbol_display})"
        )


class CompactFormatter(ResultFormatter):
    """Compact formatter for list views."""

    def format_score(self, score: float) -> str:
        pct = max(0.0, min(100.0, (1.0 - score) * 100))
        return f"{pct:.0f}%"

    def format_header(self, result: SearchResult) -> str:
        meta = result.chunk.metadata
        return f"{meta.filename}:{result.symbol_display}"


@dataclass
class SearchResultSet:
    """A collection of search results with sorting and filtering."""
    results: List[SearchResult] = field(default_factory=list)
    query: str = ""
    total_time_ms: float = 0.0
    collection_name: str = ""

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, index: int) -> SearchResult:
        return self.results[index]

    @property
    def is_empty(self) -> bool:
        return len(self.results) == 0

    @property
    def best_score(self) -> Optional[float]:
        """Return the best (lowest distance) score, or None if empty."""
        if not self.results:
            return None
        return min(r.score for r in self.results)

    @property
    def unique_paths(self) -> List[str]:
        """Get unique file paths across all results."""
        seen = set()
        paths = []
        for r in self.results:
            p = r.chunk.metadata.path
            if p not in seen:
                seen.add(p)
                paths.append(p)
        return paths

    def sort_by(self, order: SortOrder) -> "SearchResultSet":
        """Return a new result set sorted by the given order."""
        sort_keys: Dict[SortOrder, Callable] = {
            SortOrder.RELEVANCE: lambda r: r.score,
            SortOrder.PATH: lambda r: r.chunk.metadata.path,
            SortOrder.LINE_NUMBER: lambda r: r.chunk.metadata.start_line,
            SortOrder.SYMBOL: lambda r: (r.chunk.metadata.symbol or ""),
        }
        key_fn = sort_keys.get(order, sort_keys[SortOrder.RELEVANCE])
        sorted_results = sorted(self.results, key=key_fn)
        for i, r in enumerate(sorted_results):
            r.rank = i + 1
        return SearchResultSet(
            results=sorted_results,
            query=self.query,
            total_time_ms=self.total_time_ms,
            collection_name=self.collection_name,
        )

    def filter_by_type(self, chunk_type: ChunkType) -> "SearchResultSet":
        """Return results filtered to a specific chunk type."""
        filtered = [
            r for r in self.results
            if r.chunk.metadata.chunk_type == chunk_type.value
        ]
        return SearchResultSet(
            results=filtered,
            query=self.query,
            total_time_ms=self.total_time_ms,
            collection_name=self.collection_name,
        )

    def filter_by_path(self, path_substring: str) -> "SearchResultSet":
        """Return results where file path contains the given substring."""
        filtered = [
            r for r in self.results
            if path_substring in r.chunk.metadata.path
        ]
        return SearchResultSet(
            results=filtered,
            query=self.query,
            total_time_ms=self.total_time_ms,
            collection_name=self.collection_name,
        )

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Serialize all results for JSON API."""
        return [r.to_dict() for r in self.results]
