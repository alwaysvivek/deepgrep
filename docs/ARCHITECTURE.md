# 🏗️ DeepGrep Architecture

## Overview

DeepGrep is built with a modular, scalable architecture that separates concerns and enables easy extension.

## Core Principles

1. **Modularity**: Each component is independent and can be used standalone
2. **Scalability**: Horizontal scaling through stateless services
3. **Performance**: Caching, async processing, and optimized queries
4. **Maintainability**: Clean code, comprehensive tests, good documentation

---

## System Components

### 1. API Layer (`deepgrep/api/`)

**Purpose**: HTTP REST API interface

**Components**:
- `main.py`: FastAPI application with all endpoints
- `models.py`: Pydantic models for request/response validation
- `dependencies.py`: Dependency injection for shared resources

**Key Features**:
- Async endpoints for non-blocking I/O
- OpenAPI/Swagger documentation
- CORS middleware for cross-origin requests
- Request validation with Pydantic

**Example**:
```python
from fastapi import FastAPI, HTTPException
from .models import SearchRequest, SearchResponse

@app.post("/api/v1/search/regex", response_model=SearchResponse)
async def search_regex(request: SearchRequest):
    # Handle regex search
    pass
```

---

### 2. Machine Learning Layer (`deepgrep/ml/`)

**Purpose**: AI-powered semantic search

**Components**:
- `embeddings.py`: Sentence transformer embeddings
- `vector_store.py`: FAISS vector database
- `rag.py`: RAG pipeline with document chunking

**How It Works**:

1. **Text → Embeddings**
   ```python
   from deepgrep.ml import EmbeddingEngine
   
   engine = EmbeddingEngine("all-MiniLM-L6-v2")
   embeddings = engine.encode(["hello world", "search query"])
   # Returns: numpy array (2, 384)
   ```

2. **Embeddings → Vector Store**
   ```python
   from deepgrep.ml import VectorStore
   
   store = VectorStore(dimension=384)
   store.add(embeddings, documents=["hello world", "search query"])
   ```

3. **Query → Results**
   ```python
   query_emb = engine.encode("greeting")
   results = store.search(query_emb, k=10)
   # Returns: [(document, distance, metadata), ...]
   ```

**RAG Pipeline**:
```
Document → Chunking → Embeddings → Vector Store
                                          ↓
Query → Embedding → Vector Search → Top-K Results
```

---

### 3. Core Search Engine (`deepgrep/core/`)

**Purpose**: Traditional regex pattern matching

**Components**:
- `engine.py`: Main search interface
- `matcher.py`: Pattern matching state machine
- `parser.py`: Regex pattern parsing

**Pattern Flow**:
```
Pattern String → Parser → AST → Matcher → Results
```

**Example**:
```python
from deepgrep.core.engine import find_matches

matches = find_matches("test 123 data 456", r"\d+")
# Returns: ["123", "456"]
```

---

### 4. Database Layer (`deepgrep/database/`)

**Purpose**: Persistent storage with PostgreSQL

**Features**:
- SQLAlchemy ORM models
- Optimized indexes for fast queries
- Search history tracking
- Document storage

**Schema**:
```sql
search_history:
  - id (PK)
  - pattern (indexed)
  - search_type (indexed)
  - matches_count
  - timestamp (indexed)
  - files (JSON)

documents:
  - id (PK)
  - content (full-text indexed)
  - title (indexed)
  - source (indexed)
  - created_at (indexed)
  - metadata (JSON)
```

**Query Optimization**:
- Composite indexes: `(pattern, timestamp)`, `(search_type, timestamp)`
- Full-text search: GiST/GIN indexes on content
- Partitioning: Time-based partitioning for history table

---

### 5. Caching Layer (`deepgrep/cache/`)

**Purpose**: Redis-based caching for fast responses

**Use Cases**:
- Search result caching
- Embedding caching
- Session management
- Rate limiting

**Example**:
```python
from deepgrep.cache import cached

@cached("search", ttl=300)
def expensive_search(query):
    # Cached for 5 minutes
    return perform_search(query)
```

---

### 6. Background Tasks (`deepgrep/tasks/`)

**Purpose**: Asynchronous processing with Celery

**Tasks**:
- File processing
- Batch operations
- Document indexing
- Report generation

**Example**:
```python
from deepgrep.tasks import process_file_task

# Queue task
result = process_file_task.delay("/path/to/file.log", r"\d+")

# Get result
print(result.get(timeout=10))
```

---

### 7. ETL Pipeline (`deepgrep/etl/`)

**Purpose**: Extract, Transform, Load for log processing

**Pipeline Stages**:

1. **Extract**: Read log files
2. **Transform**: Parse and structure data
3. **Load**: Store in database or export

**Supported Formats**:
- Apache/Nginx logs
- JSON logs
- Generic text logs

**Example**:
```python
from deepgrep.etl import ETLPipeline

pipeline = ETLPipeline()
result = pipeline.run(
    source_path="/var/log/apache2/",
    log_format="apache",
    output_format="database"
)
```

---

### 8. Metrics Module (`deepgrep/metrics/`)

**Purpose**: Evaluate search quality

**Metrics Provided**:
- Precision
- Recall
- F1 Score
- Average Precision (AP)
- Mean Average Precision (MAP)
- NDCG
- MRR

**Example**:
```python
from deepgrep.metrics import SearchMetrics

metrics = SearchMetrics.evaluate_all(
    retrieved={1, 2, 3, 4, 5},
    relevant={2, 3, 4, 5, 6}
)
# {"precision": 0.8, "recall": 0.8, "f1_score": 0.8}
```

---

## Data Flow

### Regex Search Request

```
Client Request
    ↓
FastAPI Endpoint (/api/v1/search/regex)
    ↓
Validate Request (Pydantic)
    ↓
Check Cache (Redis)
    ↓ (cache miss)
Core Engine (find_matches)
    ↓
Store History (PostgreSQL)
    ↓
Cache Result (Redis)
    ↓
Return Response
```

### Semantic Search Request

```
Client Request
    ↓
FastAPI Endpoint (/api/v1/search/semantic)
    ↓
Validate Request (Pydantic)
    ↓
Check Cache (Redis)
    ↓ (cache miss)
RAG Pipeline
    ├─→ Generate Query Embedding
    ├─→ Chunk Documents
    ├─→ Generate Document Embeddings
    ├─→ Add to Vector Store
    └─→ Similarity Search (FAISS)
    ↓
Store History (PostgreSQL)
    ↓
Cache Result (Redis)
    ↓
Return Response
```

---

## Scalability Considerations

### Horizontal Scaling

1. **API Servers**: Stateless, can run multiple instances behind load balancer
2. **Celery Workers**: Add workers to handle more background tasks
3. **Database**: PostgreSQL read replicas for queries
4. **Redis**: Redis Cluster for distributed caching

### Performance Optimization

1. **Connection Pooling**: Reuse database connections
2. **Batch Processing**: Group operations to reduce overhead
3. **Async I/O**: Non-blocking file and network operations
4. **Index Optimization**: Proper database indexes

### Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured logging with context
- **Tracing**: Distributed tracing with OpenTelemetry

---

## Security

1. **Input Validation**: Pydantic models validate all inputs
2. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
3. **CORS**: Configurable CORS middleware
4. **Rate Limiting**: Redis-based rate limiting (can be added)
5. **Authentication**: JWT tokens (can be integrated)

---

## Extension Points

### Adding New Search Engines

```python
# deepgrep/ml/custom_engine.py
class CustomSearchEngine:
    def search(self, query: str, documents: List[str]) -> List[Match]:
        # Implement custom search logic
        pass

# deepgrep/api/main.py
@app.post("/api/v1/search/custom")
async def search_custom(request: SearchRequest):
    engine = CustomSearchEngine()
    results = engine.search(request.query, documents)
    return results
```

### Adding New ETL Sources

```python
# deepgrep/etl/sources.py
class CloudWatchLogSource:
    def extract(self, log_group: str) -> List[str]:
        # Fetch logs from CloudWatch
        pass

# Use in pipeline
pipeline = ETLPipeline()
pipeline.add_source(CloudWatchLogSource())
```

---

## Best Practices

1. **Error Handling**: Use try-except with specific exception types
2. **Logging**: Log important events with appropriate levels
3. **Testing**: Write unit tests for all modules
4. **Documentation**: Keep docs updated with code changes
5. **Code Review**: All changes go through peer review

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| API | FastAPI | Async REST API |
| ML | Sentence Transformers | Text embeddings |
| Vector DB | FAISS | Similarity search |
| Database | PostgreSQL | Persistent storage |
| Cache | Redis | Fast caching |
| Queue | Celery | Background tasks |
| Testing | Pytest | Unit/integration tests |
| CI/CD | GitHub Actions | Automation |
| Container | Docker | Containerization |

---

## Future Enhancements

1. **Multi-language Support**: Embeddings for multiple languages
2. **Real-time Search**: WebSocket support for streaming results
3. **Advanced RAG**: Integration with LLMs for question answering
4. **ML Pipelines**: MLflow for experiment tracking
5. **Observability**: OpenTelemetry integration
