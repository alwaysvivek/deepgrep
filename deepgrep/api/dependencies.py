"""API dependencies for dependency injection."""

from typing import Optional
from functools import lru_cache


@lru_cache()
def get_embedding_engine():
    """Get or create embedding engine singleton."""
    from deepgrep.ml.embeddings import EmbeddingEngine
    return EmbeddingEngine()


@lru_cache()
def get_vector_store():
    """Get or create vector store singleton."""
    from deepgrep.ml.vector_store import VectorStore
    return VectorStore(dimension=384)  # all-MiniLM-L6-v2 dimension


def get_cache():
    """Get Redis cache client."""
    # Placeholder for Redis integration
    return None


def get_db():
    """Get database session."""
    # Placeholder for PostgreSQL integration
    return None
