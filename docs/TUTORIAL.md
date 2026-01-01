# 📚 DeepGrep Tutorial

Welcome to the DeepGrep tutorial! This guide will walk you through all the features step by step.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Integration Examples](#integration-examples)

---

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn deepgrep.api.main:app --reload
```

### Your First Search

```python
import requests

# Regex search
response = requests.post("http://localhost:8000/api/v1/search/regex", json={
    "pattern": r"\d+",
    "text": "Found 42 items"
})

print(response.json())
```

---

## Basic Usage

### 1. Regex Pattern Matching

**Use Case**: Extract structured data (emails, phone numbers, dates)

```python
# Find email addresses
response = requests.post("http://localhost:8000/api/v1/search/regex", json={
    "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "text": "Contact us at support@example.com or sales@company.org"
})

# Result: ["support@example.com", "sales@company.org"]
```

### 2. Semantic Search

**Use Case**: Find contextually related content

```python
# Find similar concepts
response = requests.post("http://localhost:8000/api/v1/search/semantic", json={
    "query": "machine learning",
    "text": """
        Artificial intelligence is revolutionizing technology.
        Deep learning models can recognize patterns.
        Neural networks are powerful tools.
    """,
    "top_k": 5
})

# Result: Chunks with similarity scores
```

### 3. Batch Processing

**Use Case**: Process multiple patterns at once

```python
response = requests.post("http://localhost:8000/api/v1/search/batch", json={
    "queries": ["error", "warning", "info"],
    "text": log_content,
    "search_type": "regex"
})
```

---

## Advanced Features

### 1. RAG Pipeline with Document Chunking

```python
from deepgrep.ml import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")

# Add documents with automatic chunking
documents = [
    "First document with lots of text...",
    "Second document about different topic...",
]

pipeline.add_documents(
    documents,
    chunk_method="sentences",  # or "tokens", "paragraphs"
    chunk_size=3  # sentences per chunk
)

# Search
results = pipeline.search("your query", k=10)

for text, distance, metadata in results:
    print(f"Score: {1/(1+distance):.3f}")
    print(f"Text: {text}")
    print(f"Metadata: {metadata}\n")
```

### 2. ETL Pipeline for Log Processing

```python
from deepgrep.etl import ETLPipeline
from deepgrep.database import DatabaseManager

# Initialize with database
db = DatabaseManager("postgresql://user:pass@localhost/deepgrep")
pipeline = ETLPipeline(db_manager=db)

# Process logs
result = pipeline.run(
    source_path="/var/log/nginx/",
    log_format="apache",
    output_format="database"
)

print(f"Processed {result['total_entries']} log entries")
```

### 3. Using Celery for Background Tasks

```python
from deepgrep.tasks import process_file_task

# Queue a task
task = process_file_task.delay(
    file_path="/large/file.log",
    pattern=r"ERROR.*",
    search_type="regex"
)

# Check status
print(task.state)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocks until complete)
result = task.get(timeout=60)
print(result)
```

### 4. Caching for Performance

```python
from deepgrep.cache import cached

@cached("my_search", ttl=300)  # Cache for 5 minutes
def expensive_search(query):
    # This will only run once per unique query within 5 minutes
    return perform_expensive_operation(query)

result = expensive_search("machine learning")  # Computed
result = expensive_search("machine learning")  # From cache!
```

### 5. Search Quality Metrics

```python
from deepgrep.metrics import SearchMetrics

# Evaluate search results
retrieved_docs = {1, 2, 3, 4, 5}
relevant_docs = {2, 3, 4, 5, 6}

metrics = SearchMetrics.evaluate_all(retrieved_docs, relevant_docs)
print(f"Precision: {metrics['precision']:.2f}")
print(f"Recall: {metrics['recall']:.2f}")
print(f"F1 Score: {metrics['f1_score']:.2f}")

# Calculate MAP for multiple queries
queries_results = [
    ([1, 2, 3], {2, 3, 4}),
    ([5, 6, 7], {6, 7, 8}),
]
map_score = SearchMetrics.mean_average_precision(queries_results)
print(f"MAP: {map_score:.2f}")
```

---

## Integration Examples

### Example 1: Log Monitoring System

```python
# monitor_logs.py
import time
from deepgrep.etl import ETLPipeline
from deepgrep.database import DatabaseManager

def monitor_logs():
    db = DatabaseManager()
    pipeline = ETLPipeline(db_manager=db)
    
    while True:
        # Process new logs every minute
        pipeline.run(
            source_path="/var/log/app/",
            log_format="json",
            output_format="database"
        )
        
        # Query for errors
        errors = db.get_search_history(limit=10, search_type="error")
        if errors:
            send_alert(errors)
        
        time.sleep(60)
```

### Example 2: Semantic Document Search

```python
# document_search.py
from deepgrep.ml import RAGPipeline
import glob

def build_knowledge_base():
    pipeline = RAGPipeline()
    
    # Load all documents
    documents = []
    for file_path in glob.glob("docs/**/*.txt", recursive=True):
        with open(file_path) as f:
            documents.append(f.read())
    
    # Index documents
    pipeline.add_documents(documents, chunk_method="paragraphs")
    
    # Save for later use
    pipeline.save("knowledge_base")
    
    return pipeline

def search_knowledge_base(query):
    pipeline = RAGPipeline()
    pipeline.load("knowledge_base")
    
    results = pipeline.search(query, k=5)
    return results
```

### Example 3: FastAPI Integration

```python
# custom_api.py
from fastapi import FastAPI, BackgroundTasks
from deepgrep.ml import RAGPipeline
from deepgrep.tasks import process_file_task

app = FastAPI()
pipeline = RAGPipeline()

@app.post("/custom/search")
async def custom_search(query: str, background_tasks: BackgroundTasks):
    # Immediate response
    results = pipeline.search(query, k=10)
    
    # Queue background task
    background_tasks.add_task(log_search, query, results)
    
    return {"results": results}

def log_search(query, results):
    # Log to analytics
    pass
```

### Example 4: CLI Tool

```python
# cli.py
import click
from deepgrep.core.engine import find_matches
from deepgrep.ml import RAGPipeline

@click.group()
def cli():
    pass

@cli.command()
@click.option('--pattern', '-p', required=True)
@click.option('--file', '-f', required=True)
def regex(pattern, file):
    """Perform regex search on file."""
    with open(file) as f:
        content = f.read()
    
    matches = []
    for line in content.splitlines():
        matches.extend(find_matches(line, pattern))
    
    click.echo(f"Found {len(matches)} matches:")
    for match in matches[:10]:
        click.echo(f"  - {match}")

@cli.command()
@click.option('--query', '-q', required=True)
@click.option('--file', '-f', required=True)
def semantic(query, file):
    """Perform semantic search on file."""
    with open(file) as f:
        content = f.read()
    
    pipeline = RAGPipeline()
    pipeline.add_documents([content])
    results = pipeline.search(query, k=5)
    
    click.echo(f"Top results for '{query}':")
    for text, score, _ in results:
        click.echo(f"\nScore: {1/(1+score):.3f}")
        click.echo(f"Text: {text[:100]}...")

if __name__ == '__main__':
    cli()
```

---

## Best Practices

### 1. Chunking Strategy

Choose the right chunking method based on your data:

- **Sentences**: Good for general text, Q&A
- **Tokens**: Best for consistent chunk sizes
- **Paragraphs**: Ideal for structured documents

### 2. Embedding Model Selection

- **all-MiniLM-L6-v2**: Fast, general purpose (default)
- **all-mpnet-base-v2**: More accurate, slower
- **multi-qa-MiniLM-L6-cos-v1**: Optimized for Q&A

### 3. Database Optimization

```python
# Use connection pooling
from deepgrep.database import DatabaseManager

db = DatabaseManager("postgresql://...")

# Query with pagination
results = db.get_documents(limit=100, offset=0)

# Use indexes
# Already configured in sql/init.sql
```

### 4. Error Handling

```python
from fastapi import HTTPException

@app.post("/api/v1/search/custom")
async def search(request: SearchRequest):
    try:
        results = perform_search(request)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Troubleshooting

### Issue: Slow semantic search

**Solution**: 
- Use smaller chunk sizes
- Reduce `top_k` parameter
- Use FAISS IVF index instead of flat
- Enable caching

### Issue: High memory usage

**Solution**:
- Process files in batches
- Use Celery for large files
- Increase chunk size
- Clear vector store periodically

### Issue: Database connection errors

**Solution**:
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running
- Check connection pooling settings

---

## Next Steps

1. Explore the [API Documentation](API.md)
2. Read the [Architecture Guide](ARCHITECTURE.md)
3. Check out [example projects](../examples/)
4. Join our [community discussions](https://github.com/alwaysvivek/deepgrep/discussions)

---

## Need Help?

- 📖 Read the [full documentation](https://github.com/alwaysvivek/deepgrep/docs)
- 💬 Ask questions in [Discussions](https://github.com/alwaysvivek/deepgrep/discussions)
- 🐛 Report bugs in [Issues](https://github.com/alwaysvivek/deepgrep/issues)
- 📧 Contact: support@deepgrep.io
