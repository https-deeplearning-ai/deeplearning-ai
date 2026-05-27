"""Application configuration with environment-aware settings."""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path


class Environment(Enum):
    """Application environment modes."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class EmbeddingModel(Enum):
    """Supported embedding models for ChromaDB."""
    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    DEFAULT = "default"


@dataclass
class ChromaConfig:
    """Configuration for ChromaDB connection."""
    persist_directory: str = "./chroma_data"
    default_collection: str = "code_collection"
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    batch_size: int = 100
    max_results: int = 20

    def __post_init__(self):
        """Ensure persist directory exists."""
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)


@dataclass
class SearchConfig:
    """Configuration for search behavior."""
    default_n_results: int = 10
    max_n_results: int = 50
    min_query_length: int = 2
    max_query_length: int = 500
    score_precision: int = 4
    regex_max_results: int = 100
    regex_timeout_seconds: float = 5.0


@dataclass
class IngestionConfig:
    """Configuration for the code ingestion pipeline."""
    max_tokens_per_chunk: int = 1000
    supported_extensions: tuple = (".py",)
    ignore_patterns: tuple = ("__pycache__", ".git", ".env", "node_modules")
    batch_size: int = 100
    tokenizer_model: str = "text-embedding-3-small"
    fallback_encoding: str = "cl100k_base"


@dataclass
class ExportConfig:
    """Configuration for the export service."""
    default_format: str = "json"
    supported_formats: tuple = ("json", "csv")
    max_export_chunks: int = 10000


@dataclass
class DiffConfig:
    """Configuration for the collection diff service."""
    similarity_threshold: float = 0.98
    max_diff_results: int = 50
    include_modified_by_default: bool = True


@dataclass
class AppConfig:
    """Root application configuration combining all sub-configs."""
    environment: Environment = field(default_factory=lambda: Environment(
        os.getenv("FLASK_ENV", "development")
    ))
    secret_key: str = field(default_factory=lambda:
        os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    )
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = field(init=False)
    openai_api_key: Optional[str] = field(default_factory=lambda:
        os.getenv("OPENAI_API_KEY")
    )
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    diff: DiffConfig = field(default_factory=DiffConfig)

    def __post_init__(self):
        self.debug = self.environment == Environment.DEVELOPMENT

    @classmethod
    def from_environment(cls) -> "AppConfig":
        """Factory: build config from environment variables."""
        return cls(
            chroma=ChromaConfig(
                persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_data"),
            ),
        )


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return AppConfig.from_environment()
