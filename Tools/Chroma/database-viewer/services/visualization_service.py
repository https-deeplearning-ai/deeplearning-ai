"""Embedding space visualization service.

Provides dimensionality reduction for visualizing high-dimensional
embedding vectors as 2D scatter plots. Implements PCA from scratch
without external dependencies like numpy or scikit-learn.
"""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional

import chromadb


class ReductionMethod(Enum):
    """Available dimensionality reduction methods."""
    PCA = auto()
    RANDOM_PROJECTION = auto()


class ColorScheme(Enum):
    """How to color points in the scatter plot."""
    BY_FILE = "file"
    BY_TYPE = "type"
    BY_SYMBOL = "symbol"


@dataclass
class Point2D:
    """A single point in the 2D visualization."""
    x: float
    y: float
    chunk_id: str
    label: str
    path: str
    chunk_type: str
    symbol: str
    color_group: str = ""

    def to_dict(self) -> Dict:
        return {
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "chunk_id": self.chunk_id,
            "label": self.label,
            "path": self.path,
            "chunk_type": self.chunk_type,
            "symbol": self.symbol,
            "color_group": self.color_group,
        }


@dataclass
class PointCloud:
    """A collection of 2D points with metadata for visualization."""
    points: List[Point2D]
    method: str
    color_by: str
    x_range: Tuple[float, float] = (0.0, 0.0)
    y_range: Tuple[float, float] = (0.0, 0.0)
    variance_explained: Optional[List[float]] = None
    color_groups: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.points:
            xs = [p.x for p in self.points]
            ys = [p.y for p in self.points]
            self.x_range = (min(xs), max(xs))
            self.y_range = (min(ys), max(ys))
            # Count color groups
            groups: Dict[str, int] = {}
            for p in self.points:
                groups[p.color_group] = groups.get(p.color_group, 0) + 1
            self.color_groups = groups

    @property
    def size(self) -> int:
        return len(self.points)

    def to_dict(self) -> Dict:
        return {
            "points": [p.to_dict() for p in self.points],
            "method": self.method,
            "color_by": self.color_by,
            "size": self.size,
            "x_range": list(self.x_range),
            "y_range": list(self.y_range),
            "variance_explained": self.variance_explained,
            "color_groups": self.color_groups,
        }


class DimensionReducer(ABC):
    """Abstract base class for dimensionality reduction strategies."""

    @abstractmethod
    def reduce(self, vectors: List[List[float]]) -> List[Tuple[float, float]]:
        """Reduce high-dimensional vectors to 2D coordinates."""
        ...

    @abstractmethod
    def method_name(self) -> str:
        """Return the name of this reduction method."""
        ...


class PCAReducer(DimensionReducer):
    """Principal Component Analysis implemented from scratch.

    Computes the top-2 principal components by eigendecomposition
    of the covariance matrix using the power iteration method.
    No external math libraries required.
    """

    def method_name(self) -> str:
        return "pca"

    def reduce(self, vectors: List[List[float]]) -> List[Tuple[float, float]]:
        if len(vectors) < 2:
            return [(0.0, 0.0)] * len(vectors)

        n = len(vectors)
        d = len(vectors[0])

        # Step 1: Compute mean and center the data
        mean = self._compute_mean(vectors, n, d)
        centered = self._center_data(vectors, mean, n, d)

        # Step 2: Compute covariance matrix (d x d)
        # For high-dimensional data, use the dual trick (n x n) instead
        if d > n:
            return self._dual_pca(centered, n, d)
        else:
            return self._standard_pca(centered, n, d)

    def _standard_pca(self, centered: List[List[float]],
                      n: int, d: int) -> List[Tuple[float, float]]:
        """Standard PCA for when dimensionality <= sample count."""
        cov = self._covariance_matrix(centered, n, d)
        pc1 = self._power_iteration(cov, d)
        pc2 = self._power_iteration(cov, d, deflate_against=pc1)
        return self._project(centered, pc1, pc2)

    def _dual_pca(self, centered: List[List[float]],
                  n: int, d: int) -> List[Tuple[float, float]]:
        """Dual PCA trick for high-dimensional data (d >> n).

        Instead of eigendecomposing the d x d covariance matrix,
        eigendecompose the n x n Gram matrix: G = X @ X.T / n
        """
        # Build n x n Gram matrix
        gram = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                dot = sum(centered[i][k] * centered[j][k] for k in range(d))
                gram[i][j] = dot / n
                gram[j][i] = dot / n

        # Power iteration on Gram matrix
        ev1 = self._power_iteration(gram, n)
        ev2 = self._power_iteration(gram, n, deflate_against=ev1)

        # Project: coordinates are simply X.T @ eigenvector (scaled)
        coords = []
        for i in range(n):
            x = sum(centered[i][k] * ev1[k % len(ev1)] for k in range(min(d, n)))
            y = sum(centered[i][k] * ev2[k % len(ev2)] for k in range(min(d, n)))
            coords.append((x, y))

        return self._normalize_coords(coords)

    @staticmethod
    def _compute_mean(vectors: List[List[float]],
                      n: int, d: int) -> List[float]:
        """Compute the mean vector."""
        mean = [0.0] * d
        for vec in vectors:
            for j in range(d):
                mean[j] += vec[j]
        return [m / n for m in mean]

    @staticmethod
    def _center_data(vectors: List[List[float]], mean: List[float],
                     n: int, d: int) -> List[List[float]]:
        """Subtract the mean from each vector."""
        return [[vectors[i][j] - mean[j] for j in range(d)] for i in range(n)]

    @staticmethod
    def _covariance_matrix(centered: List[List[float]],
                           n: int, d: int) -> List[List[float]]:
        """Compute the d x d covariance matrix."""
        cov = [[0.0] * d for _ in range(d)]
        for i in range(d):
            for j in range(i, d):
                val = sum(centered[k][i] * centered[k][j] for k in range(n)) / n
                cov[i][j] = val
                cov[j][i] = val
        return cov

    @staticmethod
    def _power_iteration(matrix: List[List[float]], size: int,
                         deflate_against: Optional[List[float]] = None,
                         iterations: int = 100) -> List[float]:
        """Find the dominant eigenvector using power iteration."""
        random.seed(42)
        vec = [random.gauss(0, 1) for _ in range(size)]
        norm = math.sqrt(sum(v * v for v in vec))
        vec = [v / norm for v in vec]

        for _ in range(iterations):
            # Matrix-vector multiply
            new_vec = [0.0] * size
            for i in range(size):
                new_vec[i] = sum(matrix[i][j] * vec[j] for j in range(size))

            # Deflate to get second component
            if deflate_against is not None:
                dot = sum(new_vec[i] * deflate_against[i] for i in range(size))
                new_vec = [new_vec[i] - dot * deflate_against[i]
                           for i in range(size)]

            # Normalize
            norm = math.sqrt(sum(v * v for v in new_vec))
            if norm < 1e-10:
                break
            vec = [v / norm for v in new_vec]

        return vec

    @staticmethod
    def _project(centered: List[List[float]],
                 pc1: List[float], pc2: List[float]) -> List[Tuple[float, float]]:
        """Project centered data onto two principal components."""
        coords = []
        d = len(pc1)
        for vec in centered:
            x = sum(vec[j] * pc1[j] for j in range(d))
            y = sum(vec[j] * pc2[j] for j in range(d))
            coords.append((x, y))
        return PCAReducer._normalize_coords(coords)

    @staticmethod
    def _normalize_coords(coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Normalize coordinates to [-1, 1] range."""
        if not coords:
            return coords
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        x_range = max(xs) - min(xs) or 1.0
        y_range = max(ys) - min(ys) or 1.0
        x_mid = (max(xs) + min(xs)) / 2
        y_mid = (max(ys) + min(ys)) / 2
        return [
            ((x - x_mid) / (x_range / 2), (y - y_mid) / (y_range / 2))
            for x, y in coords
        ]


class RandomProjectionReducer(DimensionReducer):
    """Random projection for fast approximate dimensionality reduction.

    Uses a random Gaussian matrix to project from high to low dimensions.
    Based on the Johnson-Lindenstrauss lemma.
    """

    def __init__(self, seed: int = 42):
        self._seed = seed

    def method_name(self) -> str:
        return "random_projection"

    def reduce(self, vectors: List[List[float]]) -> List[Tuple[float, float]]:
        if len(vectors) < 2:
            return [(0.0, 0.0)] * len(vectors)

        d = len(vectors[0])
        random.seed(self._seed)

        # Generate two random projection vectors
        proj_x = [random.gauss(0, 1.0 / math.sqrt(d)) for _ in range(d)]
        proj_y = [random.gauss(0, 1.0 / math.sqrt(d)) for _ in range(d)]

        coords = []
        for vec in vectors:
            x = sum(vec[j] * proj_x[j] for j in range(d))
            y = sum(vec[j] * proj_y[j] for j in range(d))
            coords.append((x, y))

        return PCAReducer._normalize_coords(coords)


def get_reducer(method: ReductionMethod) -> DimensionReducer:
    """Factory function to get a dimensionality reducer."""
    reducers = {
        ReductionMethod.PCA: PCAReducer,
        ReductionMethod.RANDOM_PROJECTION: RandomProjectionReducer,
    }
    return reducers[method]()


@dataclass
class VisualizationService:
    """Service for generating 2D visualizations of embedding spaces."""
    reducer: DimensionReducer = field(default_factory=PCAReducer)

    def generate_point_cloud(
        self,
        collection: chromadb.Collection,
        color_by: ColorScheme = ColorScheme.BY_FILE,
        max_points: int = 200,
    ) -> PointCloud:
        """Generate a 2D point cloud from a collection's embeddings."""
        result = collection.get(
            limit=max_points,
            include=["embeddings", "metadatas"],
        )

        if not result["ids"]:
            return PointCloud(points=[], method=self.reducer.method_name(),
                              color_by=color_by.value)

        embeddings = result["embeddings"]
        metadatas = result["metadatas"]
        ids = result["ids"]

        # Reduce dimensions
        coords_2d = self.reducer.reduce(embeddings)

        # Build points with metadata
        points = []
        for i, (x, y) in enumerate(coords_2d):
            meta = metadatas[i]
            path = meta.get("path", "unknown")
            chunk_type = meta.get("chunk_type", "unknown")
            symbol = meta.get("symbol", "")
            filename = path.split("/")[-1] if "/" in path else path

            # Determine color group
            if color_by == ColorScheme.BY_FILE:
                group = filename
            elif color_by == ColorScheme.BY_TYPE:
                group = chunk_type
            else:
                group = symbol or "top-level"

            label = symbol if symbol else filename
            points.append(Point2D(
                x=x, y=y,
                chunk_id=ids[i],
                label=label,
                path=path,
                chunk_type=chunk_type,
                symbol=symbol,
                color_group=group,
            ))

        return PointCloud(
            points=points,
            method=self.reducer.method_name(),
            color_by=color_by.value,
        )
