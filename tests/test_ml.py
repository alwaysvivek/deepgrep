"""Tests for ML module - embeddings, vector store, and RAG pipeline."""

import pytest
import numpy as np
from deepgrep.ml.embeddings import EmbeddingEngine
from deepgrep.ml.vector_store import VectorStore
from deepgrep.ml.rag import RAGPipeline, DocumentChunker


class TestEmbeddingEngine:
    """Test embedding engine functionality."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = EmbeddingEngine("all-MiniLM-L6-v2")
        assert engine.model_name == "all-MiniLM-L6-v2"
        assert engine.embedding_dim == 384

    def test_encode_single_text(self):
        """Test encoding a single text."""
        engine = EmbeddingEngine("all-MiniLM-L6-v2")
        embedding = engine.encode("hello world")
        assert embedding.shape == (1, 384)
        assert isinstance(embedding, np.ndarray)

    def test_encode_multiple_texts(self):
        """Test encoding multiple texts."""
        engine = EmbeddingEngine("all-MiniLM-L6-v2")
        embeddings = engine.encode(["hello", "world", "test"])
        assert embeddings.shape == (3, 384)

    def test_similarity(self):
        """Test cosine similarity calculation."""
        engine = EmbeddingEngine("all-MiniLM-L6-v2")
        emb1 = engine.encode("hello world")[0]
        emb2 = engine.encode("hello world")[0]
        emb3 = engine.encode("goodbye")[0]

        # Same text should have similarity close to 1
        sim_same = engine.similarity(emb1, emb2)
        assert sim_same > 0.99

        # Different texts should have lower similarity
        sim_diff = engine.similarity(emb1, emb3)
        assert sim_diff < sim_same


class TestVectorStore:
    """Test vector store functionality."""

    def test_initialization(self):
        """Test store initialization."""
        store = VectorStore(dimension=384, index_type="flat")
        assert store.dimension == 384
        assert len(store) == 0

    def test_add_documents(self):
        """Test adding documents to store."""
        store = VectorStore(dimension=384)
        embeddings = np.random.randn(5, 384).astype(np.float32)
        documents = ["doc1", "doc2", "doc3", "doc4", "doc5"]

        store.add(embeddings, documents)
        assert len(store) == 5

    def test_search(self):
        """Test searching in vector store."""
        engine = EmbeddingEngine("all-MiniLM-L6-v2")
        store = VectorStore(dimension=384)

        # Add documents
        documents = ["hello world", "machine learning", "deep learning", "artificial intelligence"]
        embeddings = engine.encode(documents)
        store.add(embeddings, documents)

        # Search
        query_emb = engine.encode("AI and ML")
        results = store.search(query_emb, k=2)

        assert len(results) > 0
        assert all(isinstance(r[0], str) for r in results)  # document text
        assert all(isinstance(r[1], float) for r in results)  # distance


class TestDocumentChunker:
    """Test document chunking strategies."""

    def test_chunk_by_sentences(self):
        """Test sentence-based chunking."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = DocumentChunker.chunk_by_sentences(text, chunk_size=2, overlap=1)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_chunk_by_tokens(self):
        """Test token-based chunking."""
        text = " ".join(["word"] * 100)
        chunks = DocumentChunker.chunk_by_tokens(text, max_tokens=30, overlap_tokens=5)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_chunk_by_paragraphs(self):
        """Test paragraph-based chunking."""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = DocumentChunker.chunk_by_paragraphs(text, min_length=5)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)


class TestRAGPipeline:
    """Test RAG pipeline functionality."""

    def test_initialization(self):
        """Test pipeline initialization."""
        pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")
        assert pipeline.embedding_engine is not None
        assert pipeline.vector_store is not None

    def test_add_and_search(self):
        """Test adding documents and searching."""
        pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")

        # Add documents
        documents = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Python is a popular programming language for data science."
        ]
        pipeline.add_documents(documents, chunk_method="sentences")

        # Search
        results = pipeline.search("AI and neural networks", k=2)

        assert len(results) > 0
        assert all(len(r) == 3 for r in results)  # (text, distance, metadata)
