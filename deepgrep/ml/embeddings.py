"""Embedding engine using sentence-transformers."""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    """Generate embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine.

        Args:
            model_name: Name of the sentence-transformers model to use.
                      Default is 'all-MiniLM-L6-v2' - fast and efficient.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode text(s) into embeddings.

        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding

        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a search query.

        Args:
            query: Search query text

        Returns:
            numpy array of embedding (1, embedding_dim)
        """
        return self.encode(query)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
