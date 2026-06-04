"""Similarity computation service for embedding vectors.

Provides cosine similarity calculations and pairwise similarity matrices
for comparing code chunks within a ChromaDB collection.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional

import chromadb


class DistanceMetric(Enum):
    """Supported distance/similarity metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


class SimilarityComputer(ABC):
    """Abstract base class for similarity computation strategies."""

    @abstractmethod
    def compute(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute similarity between two vectors. Returns 0.0-1.0."""
        ...

    @abstractmethod
    def metric_name(self) -> str:
        """Return the name of this metric."""
        ...


class CosineSimilarity(SimilarityComputer):
    """Cosine similarity: measures the angle between two vectors.

    Returns 1.0 for identical directions, 0.0 for orthogonal vectors.
    """

    def compute(self, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b):
            raise ValueError(
                f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}"
            )

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return max(0.0, min(1.0, dot / (mag_a * mag_b)))

    def metric_name(self) -> str:
        return "cosine"


class EuclideanSimilarity(SimilarityComputer):
    """Euclidean distance converted to a 0-1 similarity score.

    Uses the formula: 1 / (1 + distance) to map distance to similarity.
    """

    def compute(self, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b):
            raise ValueError(
                f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}"
            )

        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))
        return 1.0 / (1.0 + dist)

    def metric_name(self) -> str:
        return "euclidean"


class DotProductSimilarity(SimilarityComputer):
    """Dot product similarity for normalized embeddings.

    Assumes vectors are L2-normalized; result is clamped to [0, 1].
    """

    def compute(self, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b):
            raise ValueError(
                f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}"
            )

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, dot))

    def metric_name(self) -> str:
        return "dot_product"


def get_similarity_computer(metric: DistanceMetric) -> SimilarityComputer:
    """Factory function to get a similarity computer by metric type."""
    computers = {
        DistanceMetric.COSINE: CosineSimilarity,
        DistanceMetric.EUCLIDEAN: EuclideanSimilarity,
        DistanceMetric.DOT_PRODUCT: DotProductSimilarity,
    }
    return computers[metric]()


@dataclass
class SimilarityCell:
    """A single cell in the similarity matrix."""
    row: int
    col: int
    similarity: float
    label_row: str
    label_col: str

    @property
    def percentage(self) -> float:
        return round(self.similarity * 100, 1)

    @property
    def color_intensity(self) -> int:
        """Map similarity to a 0-255 color intensity."""
        return int(self.similarity * 255)


@dataclass
class SimilarityMatrix:
    """A pairwise similarity matrix for a set of embeddings."""
    labels: List[str]
    values: List[List[float]]
    metric: str = "cosine"
    chunk_ids: List[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.labels)

    @property
    def flat_cells(self) -> List[SimilarityCell]:
        """Return all cells as a flat list for iteration."""
        cells = []
        for i in range(self.size):
            for j in range(self.size):
                cells.append(SimilarityCell(
                    row=i, col=j,
                    similarity=self.values[i][j],
                    label_row=self.labels[i],
                    label_col=self.labels[j],
                ))
        return cells

    @property
    def average_similarity(self) -> float:
        """Average off-diagonal similarity (excluding self-comparisons)."""
        if self.size < 2:
            return 0.0
        total = 0.0
        count = 0
        for i in range(self.size):
            for j in range(self.size):
                if i != j:
                    total += self.values[i][j]
                    count += 1
        return total / count if count > 0 else 0.0

    @property
    def most_similar_pair(self) -> Optional[Tuple[str, str, float]]:
        """Find the most similar pair of distinct items."""
        best = (-1.0, "", "")
        for i in range(self.size):
            for j in range(i + 1, self.size):
                if self.values[i][j] > best[0]:
                    best = (self.values[i][j], self.labels[i], self.labels[j])
        if best[0] < 0:
            return None
        return (best[1], best[2], best[0])

    @property
    def least_similar_pair(self) -> Optional[Tuple[str, str, float]]:
        """Find the least similar pair of distinct items."""
        worst = (2.0, "", "")
        for i in range(self.size):
            for j in range(i + 1, self.size):
                if self.values[i][j] < worst[0]:
                    worst = (self.values[i][j], self.labels[i], self.labels[j])
        if worst[0] > 1.0:
            return None
        return (worst[1], worst[2], worst[0])

    def to_dict(self) -> Dict:
        """Serialize for JSON API responses."""
        return {
            "labels": self.labels,
            "values": [[round(v, 4) for v in row] for row in self.values],
            "metric": self.metric,
            "size": self.size,
            "average_similarity": round(self.average_similarity, 4),
            "chunk_ids": self.chunk_ids,
        }


@dataclass
class SimilarityService:
    """Service for computing pairwise similarity between collection chunks."""
    computer: SimilarityComputer = field(default_factory=CosineSimilarity)

    def compute_matrix(
        self,
        collection: chromadb.Collection,
        chunk_ids: List[str],
    ) -> SimilarityMatrix:
        """Compute a pairwise similarity matrix for the given chunk IDs.

        Fetches embeddings from ChromaDB and builds an NxN matrix.
        """
        result = collection.get(
            ids=chunk_ids,
            include=["embeddings", "metadatas"],
        )

        embeddings = result["embeddings"]
        metadatas = result["metadatas"]
        ids = result["ids"]

        # Build labels from metadata (symbol or filename)
        labels = []
        for meta in metadatas:
            symbol = meta.get("symbol", "")
            path = meta.get("path", "unknown")
            filename = path.split("/")[-1] if "/" in path else path
            label = symbol if symbol else filename
            labels.append(label)

        n = len(embeddings)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            matrix[i][i] = 1.0  # self-similarity is always 1.0
            for j in range(i + 1, n):
                sim = self.computer.compute(embeddings[i], embeddings[j])
                matrix[i][j] = sim
                matrix[j][i] = sim  # symmetric

        return SimilarityMatrix(
            labels=labels,
            values=matrix,
            metric=self.computer.metric_name(),
            chunk_ids=ids,
        )
