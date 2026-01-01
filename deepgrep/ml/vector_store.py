"""Vector store using FAISS for efficient similarity search."""

from typing import List, Tuple, Optional
import numpy as np
import faiss
import pickle
from pathlib import Path


class VectorStore:
    """FAISS-based vector store for semantic search."""

    def __init__(self, dimension: int, index_type: str = "flat"):
        """
        Initialize the vector store.

        Args:
            dimension: Dimension of the embeddings
            index_type: Type of FAISS index ('flat', 'ivf', or 'hnsw')
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = self._create_index(index_type, dimension)
        self.documents = []  # Store original documents
        self.metadata = []  # Store metadata for each document

    def _create_index(self, index_type: str, dimension: int) -> faiss.Index:
        """Create a FAISS index based on the specified type."""
        if index_type == "flat":
            # Exact search using L2 distance
            return faiss.IndexFlatL2(dimension)
        elif index_type == "ivf":
            # Faster approximate search using inverted file index
            quantizer = faiss.IndexFlatL2(dimension)
            return faiss.IndexIVFFlat(quantizer, dimension, 100)
        elif index_type == "hnsw":
            # Hierarchical Navigable Small World graph
            return faiss.IndexHNSWFlat(dimension, 32)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

    def add(
        self,
        embeddings: np.ndarray,
        documents: List[str],
        metadata: Optional[List[dict]] = None
    ):
        """
        Add embeddings and their corresponding documents to the store.

        Args:
            embeddings: numpy array of shape (n, dimension)
            documents: List of document texts
            metadata: Optional list of metadata dictionaries
        """
        if embeddings.shape[0] != len(documents):
            raise ValueError("Number of embeddings must match number of documents")

        # Ensure embeddings are float32 (required by FAISS)
        embeddings = embeddings.astype(np.float32)

        # Train index if needed (for IVF indexes)
        if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
            self.index.train(embeddings)

        # Add to index
        self.index.add(embeddings)

        # Store documents and metadata
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float, dict]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Optional similarity threshold (lower distance = more similar)

        Returns:
            List of tuples (document, distance, metadata)
        """
        if len(self.documents) == 0:
            return []

        # Ensure query embedding is 2D and float32
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype(np.float32)

        # Search
        distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))

        # Filter and prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            if threshold is not None and dist > threshold:
                continue

            results.append((
                self.documents[idx],
                float(dist),
                self.metadata[idx]
            ))

        return results

    def save(self, path: str):
        """
        Save the vector store to disk.

        Args:
            path: Directory path to save the store
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, str(path / "index.faiss"))

        # Save documents and metadata
        with open(path / "data.pkl", "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "dimension": self.dimension,
                "index_type": self.index_type
            }, f)

    @classmethod
    def load(cls, path: str) -> "VectorStore":
        """
        Load a vector store from disk.

        Args:
            path: Directory path to load the store from

        Returns:
            Loaded VectorStore instance
        """
        path = Path(path)

        # Load data
        with open(path / "data.pkl", "rb") as f:
            data = pickle.load(f)

        # Create instance
        store = cls(data["dimension"], data["index_type"])
        store.index = faiss.read_index(str(path / "index.faiss"))
        store.documents = data["documents"]
        store.metadata = data["metadata"]

        return store

    def __len__(self) -> int:
        """Return the number of documents in the store."""
        return len(self.documents)
