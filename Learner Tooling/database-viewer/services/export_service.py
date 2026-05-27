"""Export service for collection data.

Supports exporting collection chunks to CSV and JSON formats,
with optional filtering by path, chunk type, or symbol.
"""

import csv
import io
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional

import chromadb

from services.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


class ExportFormat(ABC):
    """Abstract base for export format strategies."""

    @abstractmethod
    def serialize(self, chunks: List[Dict]) -> str:
        """Serialize a list of chunk dicts into a string."""
        ...

    @abstractmethod
    def content_type(self) -> str:
        """Return the MIME content type for this format."""
        ...

    @abstractmethod
    def file_extension(self) -> str:
        """Return the file extension for this format."""
        ...


class CSVExporter(ExportFormat):
    """Exports chunks as CSV with metadata columns."""

    COLUMNS = ["id", "document", "path", "symbol", "chunk_type", "start_line", "end_line"]

    def serialize(self, chunks: List[Dict]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.COLUMNS, extrasaction="ignore")
        writer.writeheader()

        for chunk in chunks:
            flat = {"id": chunk["id"], "document": chunk["document"]}
            flat.update(chunk.get("metadata", {}))
            writer.writerow(flat)

        return output.getvalue()

    def content_type(self) -> str:
        return "text/csv"

    def file_extension(self) -> str:
        return "csv"


class JSONExporter(ExportFormat):
    """Exports chunks as a JSON array."""

    def serialize(self, chunks: List[Dict]) -> str:
        return json.dumps(chunks, indent=2, default=str)

    def content_type(self) -> str:
        return "application/json"

    def file_extension(self) -> str:
        return "json"


def get_exporter(fmt: str) -> ExportFormat:
    """Factory: return the appropriate exporter for a format string."""
    exporters = {
        "csv": CSVExporter,
        "json": JSONExporter,
    }
    exporter_cls = exporters.get(fmt.lower())
    if exporter_cls is None:
        raise ValueError(f"Unsupported export format: {fmt}. Use one of: {list(exporters.keys())}")
    return exporter_cls()


@dataclass
class ExportResult:
    """Result of an export operation."""
    data: str
    content_type: str
    filename: str
    chunk_count: int


class ExportService:
    """Exports collection data in various formats."""

    def __init__(self):
        self._manager = get_chroma_client()

    def export_collection(self, collection_name: str, fmt: str = "json",
                          path_filter: Optional[str] = None,
                          type_filter: Optional[str] = None) -> ExportResult:
        """Export all chunks from a collection in the specified format.

        Args:
            collection_name: Name of the ChromaDB collection.
            fmt: Export format ("csv" or "json").
            path_filter: Optional file path substring filter.
            type_filter: Optional chunk type filter.

        Returns:
            ExportResult with serialized data and metadata.
        """
        logger.info(f"Exporting collection '{collection_name}' as {fmt}")

        collection = self._manager.get_existing_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection not found: {collection_name}")

        chunks = self._fetch_chunks(collection, path_filter, type_filter)

        exporter = get_exporter(fmt)
        data = exporter.serialize(chunks)

        filename = f"{collection_name}_export.{exporter.file_extension()}"

        logger.info(f"Export complete: {len(chunks)} chunks -> {filename}")

        return ExportResult(
            data=data,
            content_type=exporter.content_type(),
            filename=filename,
            chunk_count=len(chunks),
        )

    def _fetch_chunks(self, collection: chromadb.Collection,
                      path_filter: Optional[str] = None,
                      type_filter: Optional[str] = None) -> List[Dict]:
        """Fetch all chunks from a collection with optional filters."""
        get_kwargs = {"include": ["documents", "metadatas"]}

        where = self._build_where(path_filter, type_filter)
        if where:
            get_kwargs["where"] = where

        result = collection.get(**get_kwargs)

        chunks = []
        for i in range(len(result["ids"])):
            chunks.append({
                "id": result["ids"][i],
                "document": result["documents"][i],
                "metadata": result["metadatas"][i],
            })

        return chunks

    @staticmethod
    def _build_where(path_filter: Optional[str],
                     type_filter: Optional[str]) -> Optional[Dict]:
        """Build a ChromaDB where clause from filters."""
        conditions = []
        if path_filter:
            conditions.append({"path": {"$contains": path_filter}})
        if type_filter:
            conditions.append({"chunk_type": {"$eq": type_filter}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
