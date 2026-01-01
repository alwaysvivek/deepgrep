# 🚀 DeepGrep Quick Setup Guide

This guide helps you get DeepGrep running in 5 minutes!

## Prerequisites

Choose one option:

### Option A: Docker (Recommended)
- Docker Desktop or Docker Engine
- Docker Compose

### Option B: Local Development
- Python 3.9+
- PostgreSQL 12+ (optional)
- Redis 6+ (optional)

---

## Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep

# 2. Start all services
docker-compose up -d

# 3. Verify services are running
docker-compose ps

# 4. Access the API
open http://localhost:8000/docs
```

**Services running:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Celery Monitor): http://localhost:5555
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Quick Start - Local Development

```bash
# 1. Clone and setup
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API
uvicorn deepgrep.api.main:app --reload

# 5. In another terminal, start Celery (optional)
celery -A deepgrep.tasks worker --loglevel=info
```

---

## First API Call

### Using cURL

```bash
# Regex search
curl -X POST http://localhost:8000/api/v1/search/regex \
  -H "Content-Type: application/json" \
  -d '{"pattern": "\\d+", "text": "Found 42 items and 17 users"}'

# Semantic search
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "text": "AI and neural networks", "top_k": 5}'
```

### Using Python

```python
import requests

# Regex search
response = requests.post(
    "http://localhost:8000/api/v1/search/regex",
    json={"pattern": r"\d+", "text": "Found 42 items"}
)
print(response.json())

# Semantic search
response = requests.post(
    "http://localhost:8000/api/v1/search/semantic",
    json={"query": "happy", "text": "I feel joyful", "top_k": 5}
)
print(response.json())
```

### Using SDK

```python
from deepgrep.sdk.python import DeepGrepClient

client = DeepGrepClient("http://localhost:8000")

# Regex search
result = client.search_regex(r"\d+", "Found 42 items")
print(result.matches)

# Semantic search
matches = client.search_semantic("happy", text="I feel joyful")
for match in matches:
    print(f"{match.score:.3f}: {match.text}")
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=deepgrep

# Run specific test
pytest tests/test_metrics.py -v
```

---

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:
```
DATABASE_URL=postgresql://user:pass@localhost/deepgrep
REDIS_URL=redis://localhost:6379/0
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## Directory Structure

```
deepgrep/
├── deepgrep/
│   ├── api/          # FastAPI application
│   ├── core/         # Regex engine
│   ├── ml/           # ML models (embeddings, RAG, FAISS)
│   ├── database/     # PostgreSQL models
│   ├── cache/        # Redis caching
│   ├── tasks/        # Celery tasks
│   ├── etl/          # ETL pipelines
│   ├── metrics/      # Search metrics
│   └── sdk/          # Client SDKs
├── docs/             # Documentation
├── examples/         # Example scripts
├── tests/            # Test suite
└── docker-compose.yml
```

---

## Next Steps

1. **Read the docs**: See `docs/` for comprehensive guides
2. **Try examples**: Run scripts in `examples/`
3. **Explore API**: Visit http://localhost:8000/docs
4. **Join community**: https://github.com/alwaysvivek/deepgrep/discussions

---

## Troubleshooting

### Port already in use
```bash
# Stop existing services
docker-compose down

# Or change ports in docker-compose.yml
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database connection failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Or use SQLite (fallback)
DATABASE_URL=sqlite:///./deepgrep.db
```

---

## Getting Help

- 📖 **Documentation**: [docs/](docs/)
- 💬 **Discussions**: https://github.com/alwaysvivek/deepgrep/discussions
- 🐛 **Issues**: https://github.com/alwaysvivek/deepgrep/issues

---

**Ready to go!** 🎉 

Visit http://localhost:8000/docs to start exploring the API.
