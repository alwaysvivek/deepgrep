"""RAG (Retrieval-Augmented Generation) pipeline with document chunking."""

from typing import List, Tuple, Optional
import re
from .embeddings import EmbeddingEngine
from .vector_store import VectorStore


class DocumentChunker:
    """Chunk documents for better semantic search."""

    @staticmethod
    def chunk_by_sentences(
        text: str,
        chunk_size: int = 3,
        overlap: int = 1
    ) -> List[str]:
        """
        Chunk text by sentences with overlap.

        Args:
            text: Input text to chunk
            chunk_size: Number of sentences per chunk
            overlap: Number of sentences to overlap between chunks

        Returns:
            List of text chunks
        """
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks = []
        for i in range(0, len(sentences), chunk_size - overlap):
            chunk_sentences = sentences[i:i + chunk_size]
            if chunk_sentences:
                chunks.append(" ".join(chunk_sentences))

        return chunks

    @staticmethod
    def chunk_by_tokens(
        text: str,
        max_tokens: int = 512,
        overlap_tokens: int = 50
    ) -> List[str]:
        """
        Chunk text by approximate token count.

        Args:
            text: Input text to chunk
            max_tokens: Maximum tokens per chunk (approximated by words)
            overlap_tokens: Number of tokens to overlap

        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), max_tokens - overlap_tokens):
            chunk_words = words[i:i + max_tokens]
            if chunk_words:
                chunks.append(" ".join(chunk_words))

        return chunks

    @staticmethod
    def chunk_by_paragraphs(text: str, min_length: int = 100) -> List[str]:
        """
        Chunk text by paragraphs.

        Args:
            text: Input text to chunk
            min_length: Minimum character length for a chunk

        Returns:
            List of text chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            current_chunk.append(para)
            chunk_text = "\n\n".join(current_chunk)

            if len(chunk_text) >= min_length:
                chunks.append(chunk_text)
                current_chunk = []

        # Add remaining text
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for document search."""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        index_type: str = "flat"
    ):
        """
        Initialize the RAG pipeline.

        Args:
            embedding_model: Name of the sentence-transformers model
            index_type: Type of FAISS index to use
        """
        self.embedding_engine = EmbeddingEngine(embedding_model)
        self.vector_store = VectorStore(
            dimension=self.embedding_engine.embedding_dim,
            index_type=index_type
        )
        self.chunker = DocumentChunker()

    def add_documents(
        self,
        documents: List[str],
        chunk_method: str = "sentences",
        chunk_size: int = 3,
        metadata: Optional[List[dict]] = None
    ):
        """
        Add documents to the RAG pipeline with chunking.

        Args:
            documents: List of document texts
            chunk_method: Chunking method ('sentences', 'tokens', or 'paragraphs')
            chunk_size: Size parameter for chunking
            metadata: Optional metadata for each document
        """
        all_chunks = []
        all_metadata = []

        for idx, doc in enumerate(documents):
            # Chunk the document
            if chunk_method == "sentences":
                chunks = self.chunker.chunk_by_sentences(doc, chunk_size)
            elif chunk_method == "tokens":
                chunks = self.chunker.chunk_by_tokens(doc, chunk_size)
            elif chunk_method == "paragraphs":
                chunks = self.chunker.chunk_by_paragraphs(doc, chunk_size)
            else:
                raise ValueError(f"Unknown chunk method: {chunk_method}")

            # Prepare metadata
            doc_metadata = metadata[idx] if metadata else {}
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_meta = {
                    **doc_metadata,
                    "doc_id": idx,
                    "chunk_id": chunk_idx,
                    "total_chunks": len(chunks)
                }
                all_metadata.append(chunk_meta)

        # Generate embeddings
        if all_chunks:
            embeddings = self.embedding_engine.encode(all_chunks)
            self.vector_store.add(embeddings, all_chunks, all_metadata)

    def search(
        self,
        query: str,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float, dict]]:
        """
        Search for relevant document chunks.

        Args:
            query: Search query
            k: Number of results to return
            threshold: Optional similarity threshold

        Returns:
            List of tuples (chunk_text, distance, metadata)
        """
        query_embedding = self.embedding_engine.encode_query(query)
        results = self.vector_store.search(query_embedding, k, threshold)
        return results

    def save(self, path: str):
        """Save the RAG pipeline to disk."""
        self.vector_store.save(path)

    def load(self, path: str):
        """Load the RAG pipeline from disk."""
        self.vector_store = VectorStore.load(path)
