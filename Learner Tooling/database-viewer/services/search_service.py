"""Search service with semantic and regex strategies."""

import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import chromadb

logger = logging.getLogger(__name__)

from models.chunk import Chunk, ChunkMetadata
from models.search_result import SearchResult, SearchResultSet
from config import get_config


class SearchStrategy(ABC):
    """Abstract base class for search strategies."""

    @abstractmethod
    def search(self, collection: chromadb.Collection, query: str,
               n_results: int = 10, filters: Optional[Dict] = None) -> SearchResultSet:
        """Execute a search and return results."""
        ...

    @abstractmethod
    def validate_query(self, query: str) -> tuple:
        """Validate a query string. Returns (is_valid, error_message)."""
        ...


class SemanticSearchStrategy(SearchStrategy):
    """Dense/semantic search using ChromaDB's embedding-based query."""

    def validate_query(self, query: str) -> tuple:
        config = get_config().search
        if not query or not query.strip():
            return False, "Query cannot be empty"
        if len(query.strip()) < config.min_query_length:
            return False, f"Query must be at least {config.min_query_length} characters"
        if len(query.strip()) > config.max_query_length:
            return False, f"Query must be at most {config.max_query_length} characters"
        return True, ""

    def search(self, collection: chromadb.Collection, query: str,
               n_results: int = 10, filters: Optional[Dict] = None) -> SearchResultSet:
        logger.info(f"Semantic search: query='{query[:80]}' n_results={n_results} collection={collection.name}")
        start = time.time()

        where_clause = self._build_where_clause(filters) if filters else None

        query_kwargs = {
            "query_texts": [query],
            "n_results": min(n_results, get_config().search.max_n_results),
        }
        if where_clause:
            query_kwargs["where"] = where_clause

        raw = collection.query(**query_kwargs)
        elapsed_ms = (time.time() - start) * 1000

        results = []
        for i in range(len(raw["ids"][0])):
            chunk = Chunk.from_chroma_result(
                id=raw["ids"][0][i],
                document=raw["documents"][0][i],
                metadata=raw["metadatas"][0][i],
            )
            result = SearchResult(
                chunk=chunk,
                score=raw["distances"][0][i],
                rank=i + 1,
            )
            results.append(result)

        logger.info(f"Semantic search completed: {len(results)} results in {elapsed_ms:.1f}ms")

        return SearchResultSet(
            results=results,
            query=query,
            total_time_ms=elapsed_ms,
            collection_name=collection.name,
        )

    @staticmethod
    def _build_where_clause(filters: Dict) -> Optional[Dict]:
        """Build a ChromaDB where clause from filter parameters."""
        conditions = []
        if "path" in filters and filters["path"]:
            conditions.append({"path": {"$contains": filters["path"]}})
        if "chunk_type" in filters and filters["chunk_type"]:
            conditions.append({"chunk_type": {"$eq": filters["chunk_type"]}})
        if "symbol" in filters and filters["symbol"]:
            conditions.append({"symbol": {"$eq": filters["symbol"]}})
        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}


class RegexSearchStrategy(SearchStrategy):
    """Full-text regex search using ChromaDB's native where_document filter.

    Uses ChromaDB's $regex operator for server-side filtering,
    then extracts highlights and computes match-count scores client-side.
    See: https://docs.trychroma.com/docs/querying-collections/full-text-search
    """

    def validate_query(self, query: str) -> tuple:
        if not query or not query.strip():
            return False, "Pattern cannot be empty"
        try:
            re.compile(query)
        except re.error as e:
            return False, f"Invalid regex pattern: {e}"
        return True, ""

    def search(self, collection: chromadb.Collection, query: str,
               n_results: int = 50, filters: Optional[Dict] = None) -> SearchResultSet:
        logger.info(f"Regex search: pattern='{query[:80]}' collection={collection.name}")
        start = time.time()

        try:
            pattern = re.compile(query, re.MULTILINE)
        except re.error as e:
            logger.warning(f"Invalid regex pattern: {e}")
            return SearchResultSet(query=query)

        # Use ChromaDB's native full-text search with $regex operator.
        # This filters server-side instead of pulling all documents.
        matched_data = collection.get(
            where_document={"$regex": query},
            include=["documents", "metadatas"],
        )

        # Extract highlights and compute scores on the filtered results
        results = []
        for i in range(len(matched_data["ids"])):
            doc = matched_data["documents"][i]
            matches = list(pattern.finditer(doc))
            match_count = len(matches) if matches else 1

            chunk = Chunk.from_chroma_result(
                id=matched_data["ids"][i],
                document=doc,
                metadata=matched_data["metadatas"][i],
            )
            # Score: more matches = more relevant (inverted for distance convention)
            score = 1.0 / (1.0 + match_count)
            highlights = [m.group(0) for m in matches[:5]]
            results.append(SearchResult(
                chunk=chunk,
                score=score,
                highlights=highlights,
            ))

        # Sort by relevance (most matches first = lowest score)
        results.sort(key=lambda r: r.score)
        for i, r in enumerate(results[:n_results]):
            r.rank = i + 1

        elapsed_ms = (time.time() - start) * 1000

        return SearchResultSet(
            results=results[:n_results],
            query=query,
            total_time_ms=elapsed_ms,
            collection_name=collection.name,
        )


@dataclass
class SearchService:
    """Facade that dispatches to the appropriate search strategy."""
    semantic: SemanticSearchStrategy = None
    regex: RegexSearchStrategy = None

    def __post_init__(self):
        if self.semantic is None:
            self.semantic = SemanticSearchStrategy()
        if self.regex is None:
            self.regex = RegexSearchStrategy()

    def semantic_search(self, collection: chromadb.Collection, query: str,
                        n_results: int = 10, filters: Optional[Dict] = None) -> SearchResultSet:
        """Perform a semantic (dense embedding) search."""
        return self.semantic.search(collection, query, n_results, filters)

    def regex_search(self, collection: chromadb.Collection, pattern: str,
                     n_results: int = 50, filters: Optional[Dict] = None) -> SearchResultSet:
        """Perform a regex pattern search."""
        return self.regex.search(collection, pattern, n_results, filters)

    def get_strategy(self, mode: str) -> SearchStrategy:
        """Get the search strategy by name."""
        strategies = {
            "semantic": self.semantic,
            "regex": self.regex,
        }
        return strategies.get(mode, self.semantic)
