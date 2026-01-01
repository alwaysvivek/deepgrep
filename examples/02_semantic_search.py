"""
Example 2: Semantic Search with RAG

Demonstrates semantic search using the RAG pipeline.
"""

from deepgrep.ml import RAGPipeline


def build_knowledge_base():
    """Build a knowledge base from sample documents."""
    pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")
    
    documents = [
        """
        Python is a high-level, interpreted programming language known for its 
        simplicity and readability. It's widely used in web development, data 
        science, machine learning, and automation.
        """,
        """
        Machine learning is a subset of artificial intelligence that enables 
        computers to learn from data without being explicitly programmed. Popular 
        frameworks include TensorFlow, PyTorch, and scikit-learn.
        """,
        """
        Docker is a platform for developing, shipping, and running applications 
        in containers. Containers package applications with their dependencies, 
        ensuring consistency across different environments.
        """,
        """
        FastAPI is a modern, fast web framework for building APIs with Python. 
        It's based on standard Python type hints and provides automatic API 
        documentation with Swagger UI.
        """,
        """
        PostgreSQL is a powerful, open-source relational database system. It 
        features advanced indexing, full-text search, and JSON support, making 
        it suitable for complex applications.
        """
    ]
    
    # Add documents with sentence-based chunking
    pipeline.add_documents(
        documents,
        chunk_method="sentences",
        chunk_size=2
    )
    
    return pipeline


def search_knowledge_base(pipeline: RAGPipeline, query: str, k: int = 5):
    """Search the knowledge base."""
    results = pipeline.search(query, k=k)
    
    print(f"\nQuery: {query}")
    print("=" * 80)
    
    for i, (text, distance, metadata) in enumerate(results, 1):
        score = 1 / (1 + distance)  # Convert distance to similarity score
        print(f"\n{i}. Score: {score:.3f}")
        print(f"   Text: {text.strip()}")
        print(f"   Metadata: {metadata}")


if __name__ == "__main__":
    # Build knowledge base
    print("Building knowledge base...")
    pipeline = build_knowledge_base()
    print(f"Indexed {len(pipeline.vector_store)} chunks")
    
    # Perform searches
    queries = [
        "How to use containers?",
        "What is artificial intelligence?",
        "Best language for web development",
        "Database with JSON support"
    ]
    
    for query in queries:
        search_knowledge_base(pipeline, query, k=3)
