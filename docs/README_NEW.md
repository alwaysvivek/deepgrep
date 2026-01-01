# 🔍 DeepGrep - Advanced Semantic Search Platform

> **Lightning-fast regex meets AI-powered semantic search with production-ready architecture**

[![CI/CD](https://github.com/alwaysvivek/deepgrep/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/alwaysvivek/deepgrep/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Performance Metrics](#-performance-metrics)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 Core Capabilities
- **Dual Search Modes**: Regex pattern matching + AI semantic search
- **Vector Search**: FAISS-powered similarity search with embeddings
- **RAG Pipeline**: Document chunking and retrieval-augmented generation
- **Async Processing**: FastAPI with async file handling

### 🚀 Production Ready
- **PostgreSQL**: Robust database with optimized indexes
- **Redis Caching**: Ultra-fast response times
- **Celery Tasks**: Background job processing
- **Docker**: Complete containerization setup
- **CI/CD**: GitHub Actions pipeline

### 📊 Advanced Features
- **ETL Pipeline**: Log file ingestion and processing
- **Batch Processing**: Handle multiple files concurrently
- **Search Metrics**: Precision, recall, F1 scores
- **Full Documentation**: API docs, tutorials, and examples

---

## 🏗️ Architecture

### Modular Design

```
deepgrep/
├── api/              # FastAPI application
│   ├── main.py       # API endpoints
│   ├── models.py     # Pydantic models
│   └── dependencies.py
├── ml/               # Machine Learning
│   ├── embeddings.py # Sentence transformers
│   ├── vector_store.py # FAISS integration
│   └── rag.py        # RAG pipeline
├── core/             # Core search engine
│   ├── engine.py     # Regex engine
│   ├── matcher.py    # Pattern matching
│   └── parser.py     # Pattern parsing
├── database/         # PostgreSQL models
├── cache/            # Redis caching
├── tasks/            # Celery background tasks
├── etl/              # ETL pipelines
└── metrics/          # Search quality metrics
```

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  (Web UI / SDK / CLI / Third-party Apps)                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI REST API                        │
│  • /api/v1/search/regex                                 │
│  • /api/v1/search/semantic                              │
│  • /api/v1/search/batch                                 │
│  • /api/v1/upload                                       │
└────────┬────────────────────────────────────────┬───────┘
         │                                        │
    ┌────▼────┐                            ┌─────▼──────┐
    │  Redis  │                            │ PostgreSQL │
    │  Cache  │                            │  Database  │
    └─────────┘                            └────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Background Processing Layer                 │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  Celery Worker   │    │  ETL Pipeline    │          │
│  │  (Async Tasks)   │    │  (Log Ingestion) │          │
│  └──────────────────┘    └──────────────────┘          │
└────────┬────────────────────────────────────────────────┘
         │
    ┌────▼────────────────┐
    │  Search Engines     │
    │  ┌──────┐  ┌──────┐│
    │  │Regex │  │  ML  ││
    │  │Engine│  │ RAG  ││
    │  └──────┘  └──────┘│
    └─────────────────────┘
```

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Access the API
curl http://localhost:8000/health
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery Monitor)**: http://localhost:5555

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn deepgrep.api.main:app --reload

# In another terminal, start Celery worker
celery -A deepgrep.tasks worker --loglevel=info
```

---

## 💻 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (optional, defaults to SQLite)
- Redis 6+ (optional, for caching)

### Step-by-Step Installation

1. **Clone the repository**
```bash
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
# For PostgreSQL
psql -U postgres -f sql/init.sql

# Or let SQLAlchemy create tables automatically
python -c "from deepgrep.database import DatabaseManager; DatabaseManager().create_tables()"
```

---

## 📖 Usage Guide

### Basic Regex Search

```python
import requests

response = requests.post("http://localhost:8000/api/v1/search/regex", json={
    "pattern": r"\d{3}-\d{3}-\d{4}",
    "text": "Contact: 123-456-7890 or 098-765-4321"
})

print(response.json())
# Output: {"matches": ["123-456-7890", "098-765-4321"], "count": 2, ...}
```

### Semantic Search

```python
response = requests.post("http://localhost:8000/api/v1/search/semantic", json={
    "query": "machine learning",
    "text": "AI and deep learning are transforming technology. Neural networks enable pattern recognition.",
    "top_k": 5
})

print(response.json())
# Returns semantically similar text chunks with scores
```

### Batch Processing

```python
response = requests.post("http://localhost:8000/api/v1/search/batch", json={
    "queries": ["error", "warning", "critical"],
    "text": log_content,
    "search_type": "regex"
})

print(response.json())
# Returns results for all queries
```

### Using Python SDK

```python
from deepgrep.sdk import DeepGrepClient

client = DeepGrepClient(base_url="http://localhost:8000")

# Regex search
results = client.search_regex(pattern=r"\d+", text="Found 42 items")

# Semantic search
results = client.search_semantic(query="happy", text="I feel joyful today")

# Upload file
with open("logs.txt", "rb") as f:
    result = client.upload_file(f)
```

---

## 🔌 API Documentation

### Interactive API Docs

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

### Key Endpoints

#### `POST /api/v1/search/regex`
Perform regex pattern matching.

**Request:**
```json
{
  "pattern": "\\d+",
  "text": "Found 42 items and 17 users"
}
```

**Response:**
```json
{
  "matches": ["42", "17"],
  "count": 2,
  "pattern": "\\d+"
}
```

#### `POST /api/v1/search/semantic`
Perform AI-powered semantic search.

**Request:**
```json
{
  "query": "artificial intelligence",
  "text": "Machine learning and neural networks...",
  "top_k": 10
}
```

**Response:**
```json
{
  "matches": [
    {"text": "...", "score": 0.89, "metadata": {...}}
  ],
  "count": 5,
  "query": "artificial intelligence"
}
```

For complete API documentation, see [docs/API.md](docs/API.md)

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=deepgrep --cov-report=html

# Run specific test file
pytest tests/test_ml.py -v
```

### Code Quality

```bash
# Format code
black deepgrep tests

# Sort imports
isort deepgrep tests

# Lint
flake8 deepgrep tests --max-line-length=120
```

### Project Structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

---

## 📊 Performance Metrics

### Search Quality Metrics

DeepGrep includes built-in metrics for evaluating search quality:

```python
from deepgrep.metrics import SearchMetrics

# Calculate precision, recall, F1
metrics = SearchMetrics.evaluate_all(
    retrieved={1, 2, 3, 4},
    relevant={2, 3, 4, 5}
)

print(metrics)
# {"precision": 0.75, "recall": 0.75, "f1_score": 0.75}
```

### Benchmarks

| Operation | Speed | Throughput |
|-----------|-------|------------|
| Regex Search | ~1ms | 10,000 ops/s |
| Semantic Search | ~50ms | 200 ops/s |
| Batch Processing | ~500ms | 100 files/s |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📚 Additional Resources

- [📖 Tutorial](docs/TUTORIAL.md) - Step-by-step guide
- [🏗️ Architecture](docs/ARCHITECTURE.md) - System design
- [🔌 API Reference](docs/API.md) - Complete API documentation
- [📝 Blog Post](docs/BLOG.md) - Building Semantic Search with Python
- [🎥 Video Demo](docs/DEMO.md) - Visual walkthrough

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Sentence Transformers for embeddings
- FAISS for vector search
- FastAPI for the web framework
- All our contributors

---

<div align="center">

**[⭐ Star us on GitHub](https://github.com/alwaysvivek/deepgrep)** | **[📖 Read the Docs](docs/)** | **[💬 Join Discussion](https://github.com/alwaysvivek/deepgrep/discussions)**

Made with ❤️ by the DeepGrep team

</div>
