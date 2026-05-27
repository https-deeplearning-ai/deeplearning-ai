"""Query history and bookmark persistence models.

Stores search history and bookmarked results in a local JSON file,
providing a lightweight alternative to a full database for single-user apps.
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Iterator
from pathlib import Path


class SearchMode(Enum):
    """The type of search that was performed."""
    SEMANTIC = "semantic"
    REGEX = "regex"


class BookmarkColor(Enum):
    """Color labels for organizing bookmarks."""
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"


@dataclass
class QueryRecord:
    """A single search query with metadata."""
    id: str
    query: str
    mode: str
    collection: str
    result_count: int
    time_ms: float
    timestamp: str
    filters: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, query: str, mode: SearchMode, collection: str,
               result_count: int, time_ms: float,
               filters: Optional[Dict] = None) -> "QueryRecord":
        """Factory method to create a new query record with auto-generated ID."""
        return cls(
            id=str(uuid.uuid4())[:8],
            query=query,
            mode=mode.value,
            collection=collection,
            result_count=result_count,
            time_ms=round(time_ms, 1),
            timestamp=datetime.now().isoformat(),
            filters=filters or {},
        )

    @property
    def display_time(self) -> str:
        """Human-readable timestamp."""
        dt = datetime.fromisoformat(self.timestamp)
        return dt.strftime("%H:%M:%S")

    @property
    def display_date(self) -> str:
        """Human-readable date."""
        dt = datetime.fromisoformat(self.timestamp)
        return dt.strftime("%Y-%m-%d")

    @property
    def is_semantic(self) -> bool:
        return self.mode == SearchMode.SEMANTIC.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Bookmark:
    """A bookmarked search result for later reference."""
    id: str
    chunk_id: str
    collection: str
    symbol: str
    path: str
    query: str
    score: float
    color: str
    note: str
    timestamp: str

    @classmethod
    def create(cls, chunk_id: str, collection: str, symbol: str,
               path: str, query: str, score: float,
               color: BookmarkColor = BookmarkColor.YELLOW,
               note: str = "") -> "Bookmark":
        """Factory method to create a new bookmark."""
        return cls(
            id=str(uuid.uuid4())[:8],
            chunk_id=chunk_id,
            collection=collection,
            symbol=symbol,
            path=path,
            query=query,
            score=score,
            color=color.value,
            note=note,
            timestamp=datetime.now().isoformat(),
        )

    @property
    def display_time(self) -> str:
        dt = datetime.fromisoformat(self.timestamp)
        return dt.strftime("%H:%M:%S")

    @property
    def color_enum(self) -> BookmarkColor:
        try:
            return BookmarkColor(self.color)
        except ValueError:
            return BookmarkColor.YELLOW

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HistoryManager:
    """Manages query history and bookmarks with JSON file persistence.

    Implements the Repository pattern for storing and retrieving
    search history and bookmarks from a local JSON file.
    """

    DEFAULT_FILE = "search_history.json"
    MAX_HISTORY_SIZE = 100

    def __init__(self, storage_dir: Optional[str] = None):
        self._storage_dir = storage_dir or os.getcwd()
        self._file_path = os.path.join(self._storage_dir, self.DEFAULT_FILE)
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load history data from disk, or return empty structure."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"queries": [], "bookmarks": []}

    def _save(self) -> None:
        """Persist current state to disk."""
        Path(self._storage_dir).mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w") as f:
            json.dump(self._data, f, indent=2)

    # ── Query History ────────────────────────────────────────────

    def add_query(self, record: QueryRecord) -> QueryRecord:
        """Add a query to history and persist."""
        self._data["queries"].insert(0, record.to_dict())
        # Trim to max size
        if len(self._data["queries"]) > self.MAX_HISTORY_SIZE:
            self._data["queries"] = self._data["queries"][:self.MAX_HISTORY_SIZE]
        self._save()
        return record

    def get_history(self, collection: Optional[str] = None,
                    limit: int = 20) -> List[QueryRecord]:
        """Get recent query history, optionally filtered by collection."""
        records = self._data["queries"]
        if collection:
            records = [r for r in records if r.get("collection") == collection]
        return [QueryRecord(**r) for r in records[:limit]]

    def clear_history(self, collection: Optional[str] = None) -> int:
        """Clear query history. Returns the number of removed records."""
        if collection:
            before = len(self._data["queries"])
            self._data["queries"] = [
                r for r in self._data["queries"]
                if r.get("collection") != collection
            ]
            removed = before - len(self._data["queries"])
        else:
            removed = len(self._data["queries"])
            self._data["queries"] = []
        self._save()
        return removed

    def delete_query(self, query_id: str) -> bool:
        """Delete a single query record by ID."""
        before = len(self._data["queries"])
        self._data["queries"] = [
            r for r in self._data["queries"] if r.get("id") != query_id
        ]
        if len(self._data["queries"]) < before:
            self._save()
            return True
        return False

    # ── Bookmarks ────────────────────────────────────────────────

    def add_bookmark(self, bookmark: Bookmark) -> Bookmark:
        """Add a bookmark and persist."""
        # Prevent duplicate bookmarks for same chunk+collection
        self._data["bookmarks"] = [
            b for b in self._data["bookmarks"]
            if not (b.get("chunk_id") == bookmark.chunk_id
                    and b.get("collection") == bookmark.collection)
        ]
        self._data["bookmarks"].insert(0, bookmark.to_dict())
        self._save()
        return bookmark

    def get_bookmarks(self, collection: Optional[str] = None) -> List[Bookmark]:
        """Get bookmarks, optionally filtered by collection."""
        records = self._data["bookmarks"]
        if collection:
            records = [b for b in records if b.get("collection") == collection]
        return [Bookmark(**b) for b in records]

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark by ID."""
        before = len(self._data["bookmarks"])
        self._data["bookmarks"] = [
            b for b in self._data["bookmarks"] if b.get("id") != bookmark_id
        ]
        if len(self._data["bookmarks"]) < before:
            self._save()
            return True
        return False

    def is_bookmarked(self, chunk_id: str, collection: str) -> bool:
        """Check if a chunk is already bookmarked."""
        return any(
            b.get("chunk_id") == chunk_id and b.get("collection") == collection
            for b in self._data["bookmarks"]
        )

    def get_bookmark_ids(self, collection: str) -> set:
        """Get all bookmarked chunk IDs for a collection (for bulk checks)."""
        return {
            b.get("chunk_id")
            for b in self._data["bookmarks"]
            if b.get("collection") == collection
        }

    # ── Iteration ────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._data["queries"]) + len(self._data["bookmarks"])

    def __repr__(self) -> str:
        return (
            f"HistoryManager(queries={len(self._data['queries'])}, "
            f"bookmarks={len(self._data['bookmarks'])})"
        )
