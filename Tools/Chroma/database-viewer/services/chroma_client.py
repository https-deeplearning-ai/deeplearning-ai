"""ChromaDB client management with singleton pattern."""

import os
import functools
from typing import Optional, Callable, Any

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from config import AppConfig, get_config


class ChromaClientManager:
    """Singleton manager for ChromaDB PersistentClient connections.

    Ensures only one client instance exists per persist directory.
    Provides configured embedding functions for collection access.
    """

    _instance: Optional["ChromaClientManager"] = None
    _client: Optional[chromadb.ClientAPI] = None

    def __new__(cls) -> "ChromaClientManager":
        """Singleton: return existing instance or create new one."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize (only runs meaningful setup on first call)."""
        if self._client is None:
            config = get_config()
            self._config = config
            self._client = chromadb.PersistentClient(
                path=config.chroma.persist_directory
            )
            self._embedding_function = self._create_embedding_function()

    def _create_embedding_function(self) -> OpenAIEmbeddingFunction:
        """Create the OpenAI embedding function from config."""
        api_key = self._config.openai_api_key or os.getenv("CHROMA_OPENAI_API_KEY")
        return OpenAIEmbeddingFunction(
            model_name=self._config.chroma.embedding_model.value,
            api_key=api_key,
            api_key_env_var="OPENAI_API_KEY",
        )

    @property
    def client(self) -> chromadb.ClientAPI:
        """Access the underlying ChromaDB client."""
        return self._client

    @property
    def embedding_function(self) -> OpenAIEmbeddingFunction:
        """Access the configured embedding function."""
        return self._embedding_function

    def get_collection(self, name: str) -> chromadb.Collection:
        """Get or create a collection with the configured embedding function."""
        return self._client.get_or_create_collection(
            name=name,
            embedding_function=self._embedding_function,
        )

    def get_existing_collection(self, name: str) -> Optional[chromadb.Collection]:
        """Get a collection only if it exists; return None otherwise."""
        try:
            return self._client.get_collection(
                name=name,
                embedding_function=self._embedding_function,
            )
        except Exception:
            return None

    def list_collections(self) -> list:
        """List all available collections."""
        return self._client.list_collections()

    def delete_collection(self, name: str) -> bool:
        """Delete a collection by name. Returns True if deleted."""
        try:
            self._client.delete_collection(name)
            return True
        except Exception:
            return False

    def heartbeat(self) -> int:
        """Check ChromaDB connectivity. Returns heartbeat timestamp."""
        return self._client.heartbeat()

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None
        cls._client = None


def get_chroma_client() -> ChromaClientManager:
    """Convenience function to get the ChromaDB client manager."""
    return ChromaClientManager()


def require_collection(f: Callable) -> Callable:
    """Decorator: injects a ChromaDB collection into the wrapped function.

    The decorated function must accept 'collection_name' as a keyword arg.
    The decorator resolves it to an actual collection object passed as 'collection'.
    """
    @functools.wraps(f)
    def wrapper(*args, collection_name: str = "", **kwargs) -> Any:
        if not collection_name:
            raise ValueError("collection_name is required")
        manager = get_chroma_client()
        collection = manager.get_existing_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection not found: {collection_name}")
        kwargs["collection"] = collection
        return f(*args, **kwargs)
    return wrapper
