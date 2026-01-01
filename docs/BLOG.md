# Building Semantic Search with Python: A Complete Guide

**By DeepGrep Team | January 2026**

---

## Introduction

In the age of information overload, finding relevant content quickly is crucial. Traditional keyword search often falls short when dealing with natural language queries. Enter **semantic search** – a technique that understands the *meaning* behind queries, not just matching keywords.

In this post, we'll build a production-ready semantic search system using Python, covering embeddings, vector databases, and the RAG (Retrieval-Augmented Generation) pattern.

## What is Semantic Search?

Semantic search goes beyond keyword matching by understanding:
- **Context**: "bank" in "river bank" vs "money bank"
- **Synonyms**: "happy" matches "joyful" and "delighted"
- **Intent**: "How to install Python?" finds installation guides

### How It Works

```
Text → Embeddings → Vector Store → Similarity Search
```

1. **Embeddings**: Convert text to numerical vectors
2. **Vector Store**: Efficiently store and index vectors
3. **Similarity Search**: Find nearest neighbors in vector space

## Building the System

### Step 1: Text Embeddings

We use **Sentence Transformers** for generating embeddings:

```python
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts):
        """Convert texts to embeddings."""
        return self.model.encode(texts, convert_to_numpy=True)
```

**Why all-MiniLM-L6-v2?**
- Fast: 384-dimensional vectors
- Accurate: State-of-the-art quality
- Lightweight: Only 80MB

### Step 2: Vector Database with FAISS

**FAISS** (Facebook AI Similarity Search) enables ultra-fast similarity search:

```python
import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
    
    def add(self, embeddings, documents):
        """Add embeddings to the index."""
        embeddings = embeddings.astype(np.float32)
        self.index.add(embeddings)
        self.documents.extend(documents)
    
    def search(self, query_embedding, k=10):
        """Search for similar documents."""
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        
        return results
```

### Step 3: Document Chunking

Large documents need to be split into smaller chunks for better search:

```python
import re

class DocumentChunker:
    @staticmethod
    def chunk_by_sentences(text, chunk_size=3, overlap=1):
        """Split text into overlapping sentence chunks."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        for i in range(0, len(sentences), chunk_size - overlap):
            chunk = " ".join(sentences[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
```

**Why Chunking?**
- Improves precision
- Better context preservation
- Enables granular search

### Step 4: RAG Pipeline

Bringing it all together:

```python
class RAGPipeline:
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.vector_store = VectorStore(dimension=384)
        self.chunker = DocumentChunker()
    
    def add_documents(self, documents, chunk_size=3):
        """Index documents for search."""
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunker.chunk_by_sentences(doc, chunk_size)
            all_chunks.extend(chunks)
        
        embeddings = self.embedding_engine.encode(all_chunks)
        self.vector_store.add(embeddings, all_chunks)
    
    def search(self, query, k=10):
        """Search for relevant chunks."""
        query_embedding = self.embedding_engine.encode([query])
        results = self.vector_store.search(query_embedding, k)
        return results
```

## Real-World Example

Let's build a documentation search system:

```python
# Initialize pipeline
pipeline = RAGPipeline()

# Add documentation
docs = [
    """
    Python is a high-level programming language known for its simplicity.
    It's widely used in web development, data science, and automation.
    """,
    """
    Machine learning enables computers to learn from data without explicit programming.
    Popular frameworks include TensorFlow, PyTorch, and scikit-learn.
    """,
    """
    Docker containers package applications with their dependencies.
    This ensures consistency across development, testing, and production environments.
    """
]

pipeline.add_documents(docs)

# Search
results = pipeline.search("How to use containers?", k=3)

for text, distance in results:
    similarity = 1 / (1 + distance)  # Convert distance to similarity
    print(f"Similarity: {similarity:.3f}")
    print(f"Text: {text}\n")
```

Output:
```
Similarity: 0.892
Text: Docker containers package applications with their dependencies.
      This ensures consistency across development...

Similarity: 0.654
Text: Python is a high-level programming language...

Similarity: 0.598
Text: Machine learning enables computers to learn...
```

## Performance Optimization

### 1. Index Selection

FAISS offers multiple index types:

```python
# Fast but memory-intensive
index = faiss.IndexFlatL2(dimension)

# Memory-efficient with approximate search
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)

# Best for large datasets
index = faiss.IndexHNSWFlat(dimension, M=32)
```

### 2. Caching

Cache embeddings to avoid recomputation:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str):
    return embedding_engine.encode([text])[0]
```

### 3. Batch Processing

Process multiple queries at once:

```python
def batch_search(queries, k=10):
    # Encode all queries together
    query_embeddings = embedding_engine.encode(queries)
    
    # Search in parallel
    results = []
    for emb in query_embeddings:
        results.append(vector_store.search(emb, k))
    
    return results
```

## Production Considerations

### Scalability

1. **Horizontal Scaling**: Run multiple instances behind a load balancer
2. **Async Processing**: Use FastAPI for non-blocking I/O
3. **Distributed Storage**: Store vectors in a distributed database

### Monitoring

Track key metrics:

```python
from deepgrep.metrics import SearchMetrics

# Evaluate search quality
retrieved = {1, 2, 3, 4, 5}
relevant = {2, 3, 4, 5, 6}

metrics = SearchMetrics.evaluate_all(retrieved, relevant)
print(f"Precision: {metrics['precision']:.2f}")
print(f"Recall: {metrics['recall']:.2f}")
print(f"F1 Score: {metrics['f1_score']:.2f}")
```

### API Design

Expose through a REST API:

```python
from fastapi import FastAPI

app = FastAPI()
pipeline = RAGPipeline()

@app.post("/search")
async def search(query: str, k: int = 10):
    results = pipeline.search(query, k)
    return {
        "query": query,
        "results": [
            {"text": text, "score": 1/(1+dist)}
            for text, dist in results
        ]
    }
```

## Advanced Topics

### Multi-Language Support

Use multilingual models:

```python
# Supports 50+ languages
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

### Domain-Specific Embeddings

Fine-tune on your domain:

```python
from sentence_transformers import SentenceTransformer, InputExample, losses

model = SentenceTransformer('all-MiniLM-L6-v2')

# Create training examples
train_examples = [
    InputExample(texts=['query', 'positive doc'], label=1.0),
    InputExample(texts=['query', 'negative doc'], label=0.0),
]

# Train
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1)
```

### Hybrid Search

Combine semantic and keyword search:

```python
def hybrid_search(query, k=10, alpha=0.5):
    # Semantic search
    semantic_results = pipeline.search(query, k)
    
    # Keyword search (BM25)
    keyword_results = bm25_search(query, k)
    
    # Combine scores
    combined = {}
    for doc, score in semantic_results:
        combined[doc] = alpha * score
    
    for doc, score in keyword_results:
        combined[doc] = combined.get(doc, 0) + (1 - alpha) * score
    
    # Sort by combined score
    return sorted(combined.items(), key=lambda x: x[1], reverse=True)[:k]
```

## Conclusion

We've built a complete semantic search system with:

✅ **Embeddings**: Using Sentence Transformers  
✅ **Vector Store**: FAISS for fast similarity search  
✅ **RAG Pipeline**: Document chunking and retrieval  
✅ **Production Ready**: API, caching, monitoring  

The complete code is available at [DeepGrep GitHub](https://github.com/alwaysvivek/deepgrep).

## Next Steps

1. Experiment with different embedding models
2. Try various chunking strategies
3. Implement hybrid search
4. Add query expansion
5. Fine-tune on your domain

## Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [DeepGrep Project](https://github.com/alwaysvivek/deepgrep)

---

**Questions?** Join the discussion on [GitHub Discussions](https://github.com/alwaysvivek/deepgrep/discussions)

**Found this helpful?** Star the project on [GitHub](https://github.com/alwaysvivek/deepgrep)! ⭐
