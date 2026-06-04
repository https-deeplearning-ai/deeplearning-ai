"""Collection management service for ChromaDB."""

import logging
import functools
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from services.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


def log_operation(operation_name: str):
    """Decorator factory: logs service operations with timing."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Failed: {operation_name} - {e}")
                raise
        return wrapper
    return decorator


@dataclass
class CollectionStats:
    """Statistics about a ChromaDB collection."""
    name: str
    count: int
    unique_files: int = 0
    unique_symbols: int = 0
    chunk_types: Dict[str, int] = field(default_factory=dict)
    file_list: List[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    @property
    def summary(self) -> str:
        """One-line summary string."""
        return f"{self.name}: {self.count} chunks across {self.unique_files} files"


@dataclass
class CollectionInfo:
    """Lightweight collection info for listing."""
    name: str
    count: int

    @classmethod
    def from_collection(cls, collection) -> "CollectionInfo":
        return cls(name=collection.name, count=collection.count())


class CollectionService:
    """Service for managing ChromaDB collections."""

    def __init__(self):
        self._manager = get_chroma_client()

    @log_operation("list_collections")
    def list_collections(self) -> List[CollectionInfo]:
        """List all collections with basic info."""
        collections = self._manager.list_collections()
        result = []
        for coll in collections:
            try:
                info = CollectionInfo(name=coll.name, count=coll.count())
                result.append(info)
            except Exception:
                result.append(CollectionInfo(name=coll.name, count=0))
        return result

    @log_operation("get_collection_stats")
    def get_collection_stats(self, name: str) -> Optional[CollectionStats]:
        """Get detailed statistics for a collection."""
        collection = self._manager.get_existing_collection(name)
        if collection is None:
            return None

        count = collection.count()
        if count == 0:
            return CollectionStats(name=name, count=0)

        all_data = collection.get(include=["metadatas"])
        paths = set()
        symbols = set()
        chunk_types: Dict[str, int] = {}

        for meta in all_data["metadatas"]:
            path = meta.get("path", "unknown")
            paths.add(path)
            symbol = meta.get("symbol")
            if symbol:
                symbols.add(symbol)
            ct = meta.get("chunk_type", "unknown")
            chunk_types[ct] = chunk_types.get(ct, 0) + 1

        return CollectionStats(
            name=name,
            count=count,
            unique_files=len(paths),
            unique_symbols=len(symbols),
            chunk_types=chunk_types,
            file_list=sorted(paths),
        )

    @log_operation("create_collection")
    def create_collection(self, name: str) -> bool:
        """Create a new empty collection."""
        try:
            self._manager.get_collection(name)
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    @log_operation("delete_collection")
    def delete_collection(self, name: str) -> bool:
        """Delete a collection by name."""
        return self._manager.delete_collection(name)

    def get_chunks_page(self, name: str, offset: int = 0, limit: int = 20,
                        path_filter: Optional[str] = None,
                        type_filter: Optional[str] = None,
                        symbol_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get a paginated page of chunks from a collection with optional filters."""
        collection = self._manager.get_existing_collection(name)
        if collection is None:
            return {"chunks": [], "total": 0, "offset": offset, "limit": limit}

        where = self._build_filter_clause(path_filter, type_filter, symbol_filter)

        get_kwargs: Dict[str, Any] = {"include": ["documents", "metadatas"]}
        if where:
            get_kwargs["where"] = where

        get_kwargs["limit"] = limit
        get_kwargs["offset"] = offset

        data = collection.get(**get_kwargs)

        chunks = []
        for i in range(len(data["ids"])):
            chunks.append({
                "id": data["ids"][i],
                "document": data["documents"][i],
                "metadata": data["metadatas"][i],
            })

        return {
            "chunks": chunks,
            "total": collection.count(),
            "offset": offset,
            "limit": limit,
        }

    @staticmethod
    def _build_filter_clause(path_filter: Optional[str],
                              type_filter: Optional[str],
                              symbol_filter: Optional[str]) -> Optional[Dict]:
        """Build ChromaDB where clause from optional filter parameters."""
        conditions = []
        if path_filter:
            conditions.append({"path": {"$contains": path_filter}})
        if type_filter:
            conditions.append({"chunk_type": {"$eq": type_filter}})
        if symbol_filter:
            conditions.append({"symbol": {"$eq": symbol_filter}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
