"""Code statistics analysis service.

Provides detailed code metrics and analytics for collections,
including line counts, token estimates, complexity scoring,
chunk size distributions, duplicate detection, and code construct detection.
"""

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple

import chromadb

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories for organizing computed metrics."""
    OVERVIEW = auto()
    SIZE = auto()
    COMPLEXITY = auto()
    STRUCTURE = auto()


class CodeConstruct(Enum):
    """Detectable Python code constructs."""
    CLASS = "class"
    FUNCTION = "function"
    ASYNC_FUNCTION = "async function"
    DECORATOR = "decorator"
    DATACLASS = "dataclass"
    ENUM_CLASS = "enum"
    ABC_CLASS = "abstract class"
    PROPERTY = "property"
    STATIC_METHOD = "static method"
    CLASS_METHOD = "class method"
    DUNDER_METHOD = "dunder method"
    IMPORT = "import"
    EXCEPTION_HANDLER = "try/except"
    COMPREHENSION = "comprehension"
    TYPE_HINT = "type hint"


@dataclass
class ConstructCount:
    """Count of a specific code construct."""
    construct: CodeConstruct
    count: int
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "construct": self.construct.value,
            "count": self.count,
            "examples": self.examples[:5],
        }


@dataclass
class FileMetrics:
    """Metrics for a single file in the collection."""
    path: str
    chunk_count: int
    total_lines: int
    total_chars: int
    symbols: List[str] = field(default_factory=list)
    chunk_types: Dict[str, int] = field(default_factory=dict)

    @property
    def avg_lines_per_chunk(self) -> float:
        if self.chunk_count == 0:
            return 0.0
        return self.total_lines / self.chunk_count

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "filename": self.path.split("/")[-1] if "/" in self.path else self.path,
            "chunk_count": self.chunk_count,
            "total_lines": self.total_lines,
            "total_chars": self.total_chars,
            "avg_lines_per_chunk": round(self.avg_lines_per_chunk, 1),
            "symbols": self.symbols,
            "symbol_count": len(self.symbols),
            "chunk_types": self.chunk_types,
        }


@dataclass
class SizeDistribution:
    """Distribution of chunk sizes for histogram rendering."""
    bucket_labels: List[str] = field(default_factory=list)
    bucket_counts: List[int] = field(default_factory=list)
    min_lines: int = 0
    max_lines: int = 0
    median_lines: float = 0.0
    mean_lines: float = 0.0
    std_dev: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "buckets": [
                {"label": l, "count": c}
                for l, c in zip(self.bucket_labels, self.bucket_counts)
            ],
            "min": self.min_lines,
            "max": self.max_lines,
            "median": self.median_lines,
            "mean": round(self.mean_lines, 1),
            "std_dev": round(self.std_dev, 1),
        }


@dataclass
class CollectionStatistics:
    """Complete statistics report for a collection."""
    collection_name: str
    total_chunks: int = 0
    total_lines: int = 0
    total_chars: int = 0
    total_files: int = 0
    total_symbols: int = 0
    file_metrics: List[FileMetrics] = field(default_factory=list)
    chunk_type_counts: Dict[str, int] = field(default_factory=dict)
    construct_counts: List[ConstructCount] = field(default_factory=list)
    size_distribution: Optional[SizeDistribution] = None
    top_symbols: List[Dict] = field(default_factory=list)
    token_stats: Optional[Dict] = None
    duplicate_groups: List[Dict] = field(default_factory=list)

    @property
    def avg_lines_per_file(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.total_lines / self.total_files

    @property
    def avg_chunks_per_file(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.total_chunks / self.total_files

    @property
    def construct_summary(self) -> Dict[str, int]:
        """Flat map of construct name -> count."""
        return {c.construct.value: c.count for c in self.construct_counts if c.count > 0}

    def to_dict(self) -> Dict:
        return {
            "collection": self.collection_name,
            "overview": {
                "total_chunks": self.total_chunks,
                "total_lines": self.total_lines,
                "total_chars": self.total_chars,
                "total_files": self.total_files,
                "total_symbols": self.total_symbols,
                "avg_lines_per_file": round(self.avg_lines_per_file, 1),
                "avg_chunks_per_file": round(self.avg_chunks_per_file, 1),
            },
            "chunk_types": self.chunk_type_counts,
            "constructs": [c.to_dict() for c in self.construct_counts if c.count > 0],
            "construct_summary": self.construct_summary,
            "size_distribution": self.size_distribution.to_dict() if self.size_distribution else None,
            "files": [f.to_dict() for f in self.file_metrics],
            "top_symbols": self.top_symbols,
            "token_stats": self.token_stats,
            "duplicates": self.duplicate_groups,
        }


class MetricComputer(ABC):
    """Abstract base for metric computation strategies."""

    @abstractmethod
    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        """Compute metrics from documents and metadata."""
        ...

    @abstractmethod
    def metric_name(self) -> str:
        """Return the name of this metric."""
        ...


class ConstructDetector(MetricComputer):
    """Detects Python code constructs using regex patterns.

    Scans all document text for common Python constructs
    like classes, decorators, comprehensions, and type hints.
    """

    PATTERNS: List[Tuple[CodeConstruct, str]] = [
        (CodeConstruct.DATACLASS, r"@dataclass"),
        (CodeConstruct.ENUM_CLASS, r"class\s+\w+\(.*Enum.*\)"),
        (CodeConstruct.ABC_CLASS, r"class\s+\w+\(.*ABC.*\)"),
        (CodeConstruct.ASYNC_FUNCTION, r"async\s+def\s+(\w+)"),
        (CodeConstruct.DECORATOR, r"@(\w+)"),
        (CodeConstruct.PROPERTY, r"@property"),
        (CodeConstruct.STATIC_METHOD, r"@staticmethod"),
        (CodeConstruct.CLASS_METHOD, r"@classmethod"),
        (CodeConstruct.DUNDER_METHOD, r"def\s+(__\w+__)"),
        (CodeConstruct.CLASS, r"class\s+(\w+)"),
        (CodeConstruct.FUNCTION, r"def\s+(\w+)"),
        (CodeConstruct.IMPORT, r"(?:from|import)\s+\w+"),
        (CodeConstruct.EXCEPTION_HANDLER, r"\btry\s*:"),
        (CodeConstruct.COMPREHENSION, r"\[.*\bfor\b.*\bin\b.*\]"),
        (CodeConstruct.TYPE_HINT, r":\s*(?:List|Dict|Optional|Tuple|Set|str|int|float|bool)\b"),
    ]

    def metric_name(self) -> str:
        return "construct_detection"

    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        all_text = "\n".join(documents)
        counts: List[ConstructCount] = []

        for construct, pattern in self.PATTERNS:
            matches = re.findall(pattern, all_text)
            examples = []
            if matches:
                # Extract unique named examples
                seen = set()
                for m in matches:
                    name = m if isinstance(m, str) else str(m)
                    if name not in seen and len(name) > 1:
                        seen.add(name)
                        examples.append(name)

            counts.append(ConstructCount(
                construct=construct,
                count=len(matches),
                examples=examples[:5],
            ))

        return {"constructs": counts}


class SizeAnalyzer(MetricComputer):
    """Analyzes chunk size distribution.

    Computes histogram buckets, percentiles, and statistical
    measures of code chunk sizes for distribution visualization.
    """

    BUCKET_RANGES: List[Tuple[int, int, str]] = [
        (1, 5, "1-5"),
        (6, 10, "6-10"),
        (11, 20, "11-20"),
        (21, 40, "21-40"),
        (41, 80, "41-80"),
        (81, 150, "81-150"),
        (151, 9999, "150+"),
    ]

    def metric_name(self) -> str:
        return "size_analysis"

    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        line_counts = [doc.count("\n") + 1 for doc in documents]

        if not line_counts:
            return {"distribution": SizeDistribution()}

        # Build histogram
        labels = []
        counts = []
        for low, high, label in self.BUCKET_RANGES:
            labels.append(label)
            counts.append(sum(1 for lc in line_counts if low <= lc <= high))

        sorted_lines = sorted(line_counts)
        n = len(sorted_lines)
        mean = sum(sorted_lines) / n
        median = sorted_lines[n // 2] if n % 2 else (sorted_lines[n // 2 - 1] + sorted_lines[n // 2]) / 2
        variance = sum((x - mean) ** 2 for x in sorted_lines) / n
        std_dev = variance ** 0.5

        dist = SizeDistribution(
            bucket_labels=labels,
            bucket_counts=counts,
            min_lines=sorted_lines[0],
            max_lines=sorted_lines[-1],
            median_lines=median,
            mean_lines=mean,
            std_dev=std_dev,
        )

        return {"distribution": dist}


class SymbolRanker(MetricComputer):
    """Ranks symbols by code size and complexity.

    Identifies the largest and most complex symbols in the
    collection for the "top symbols" leaderboard display.
    """

    def metric_name(self) -> str:
        return "symbol_ranking"

    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        symbol_data: Dict[str, Dict] = {}

        for doc, meta in zip(documents, metadatas):
            symbol = meta.get("symbol", "")
            if not symbol:
                continue

            lines = doc.count("\n") + 1
            chars = len(doc)
            path = meta.get("path", "unknown")

            if symbol not in symbol_data:
                symbol_data[symbol] = {
                    "symbol": symbol,
                    "lines": 0,
                    "chars": 0,
                    "path": path,
                    "chunk_type": meta.get("chunk_type", ""),
                    "chunks": 0,
                }

            symbol_data[symbol]["lines"] += lines
            symbol_data[symbol]["chars"] += chars
            symbol_data[symbol]["chunks"] += 1

        # Sort by lines descending
        ranked = sorted(symbol_data.values(), key=lambda s: s["lines"], reverse=True)
        return {"top_symbols": ranked[:15]}


class TokenEstimator(MetricComputer):
    """Estimates token usage across chunks.

    Uses a character-based heuristic (chars / 4) to approximate
    token counts without requiring a tokenizer dependency, then
    computes per-chunk statistics for cost estimation.
    """

    CHARS_PER_TOKEN = 4

    def metric_name(self) -> str:
        return "token_estimation"

    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        if not documents:
            return {"token_stats": None}

        token_counts = [len(doc) // self.CHARS_PER_TOKEN for doc in documents]
        total = sum(token_counts)
        mean = total / len(token_counts)
        sorted_counts = sorted(token_counts)
        n = len(sorted_counts)
        median = sorted_counts[n // 2] if n % 2 else (sorted_counts[n // 2 - 1] + sorted_counts[n // 2]) / 2

        return {
            "token_stats": {
                "total_estimated_tokens": total,
                "avg_tokens_per_chunk": round(mean, 1),
                "median_tokens_per_chunk": median,
                "min_tokens": sorted_counts[0],
                "max_tokens": sorted_counts[-1],
            }
        }


class DuplicateDetector(MetricComputer):
    """Detects duplicate and near-duplicate chunks.

    Uses content hashing to find exact duplicates. Chunks with
    identical normalized content are grouped together, which can
    indicate redundant indexing or overlapping file processing.
    """

    def metric_name(self) -> str:
        return "duplicate_detection"

    def compute(self, documents: List[str], metadatas: List[Dict]) -> Dict:
        hash_to_indices: Dict[str, List[int]] = {}

        for i, doc in enumerate(documents):
            normalized = doc.strip()
            content_hash = hashlib.md5(normalized.encode("utf-8")).hexdigest()

            if content_hash not in hash_to_indices:
                hash_to_indices[content_hash] = []
            hash_to_indices[content_hash].append(i)

        duplicate_groups = []
        for content_hash, indices in hash_to_indices.items():
            if len(indices) < 2:
                continue

            paths = [metadatas[i].get("path", "unknown") for i in indices]
            symbols = [metadatas[i].get("symbol", "") for i in indices]

            duplicate_groups.append({
                "count": len(indices),
                "paths": list(set(paths)),
                "symbols": [s for s in set(symbols) if s],
                "preview": documents[indices[0]][:120],
            })

        duplicate_groups.sort(key=lambda g: g["count"], reverse=True)

        logger.info(f"Duplicate detection: found {len(duplicate_groups)} groups")

        return {"duplicate_groups": duplicate_groups[:20]}


@dataclass
class StatisticsService:
    """Orchestrates code statistics computation.

    Combines multiple metric computers to produce a comprehensive
    statistics report for a collection's code content.
    """
    computers: List[MetricComputer] = field(default_factory=lambda: [
        ConstructDetector(),
        SizeAnalyzer(),
        SymbolRanker(),
        TokenEstimator(),
        DuplicateDetector(),
    ])

    def compute_statistics(self, collection: chromadb.Collection) -> CollectionStatistics:
        """Compute full statistics for a collection."""
        result = collection.get(include=["documents", "metadatas"])

        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])
        ids = result.get("ids", [])

        if not ids:
            return CollectionStatistics(collection_name=collection.name)

        # Basic counts
        stats = CollectionStatistics(
            collection_name=collection.name,
            total_chunks=len(ids),
        )

        # Per-file aggregation
        file_data: Dict[str, FileMetrics] = {}
        all_symbols = set()

        for doc, meta in zip(documents, metadatas):
            path = meta.get("path", "unknown")
            symbol = meta.get("symbol", "")
            chunk_type = meta.get("chunk_type", "unknown")
            lines = doc.count("\n") + 1
            chars = len(doc)

            stats.total_lines += lines
            stats.total_chars += chars
            stats.chunk_type_counts[chunk_type] = stats.chunk_type_counts.get(chunk_type, 0) + 1

            if symbol:
                all_symbols.add(symbol)

            if path not in file_data:
                file_data[path] = FileMetrics(path=path, chunk_count=0, total_lines=0, total_chars=0)

            fm = file_data[path]
            fm.chunk_count += 1
            fm.total_lines += lines
            fm.total_chars += chars
            if symbol:
                fm.symbols.append(symbol)
            fm.chunk_types[chunk_type] = fm.chunk_types.get(chunk_type, 0) + 1

        stats.total_files = len(file_data)
        stats.total_symbols = len(all_symbols)
        stats.file_metrics = sorted(file_data.values(), key=lambda f: f.total_lines, reverse=True)

        # Run metric computers
        for computer in self.computers:
            computed = computer.compute(documents, metadatas)

            if "constructs" in computed:
                stats.construct_counts = computed["constructs"]
            if "distribution" in computed:
                stats.size_distribution = computed["distribution"]
            if "top_symbols" in computed:
                stats.top_symbols = computed["top_symbols"]
            if "token_stats" in computed:
                stats.token_stats = computed["token_stats"]
            if "duplicate_groups" in computed:
                stats.duplicate_groups = computed["duplicate_groups"]

        return stats
