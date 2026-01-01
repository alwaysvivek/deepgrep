# 🎥 DeepGrep Demo & Walkthrough

## Video Demo Script

This document provides a script for creating a video demo or following along with the DeepGrep features.

---

## Part 1: Introduction (0:00 - 1:00)

**Screen**: Show DeepGrep logo and tagline

**Narration**:
> "Welcome to DeepGrep - the advanced semantic search platform that combines lightning-fast regex with AI-powered semantic search. In this demo, we'll explore all the features that make DeepGrep production-ready."

**Screen**: Show architecture diagram

---

## Part 2: Quick Start (1:00 - 3:00)

### Step 1: Installation

**Screen**: Terminal with commands

```bash
# Clone the repository
git clone https://github.com/alwaysvivek/deepgrep.git
cd deepgrep

# Start with Docker (recommended)
docker-compose up -d
```

**Narration**:
> "Getting started is easy. Clone the repo and start all services with Docker Compose. This launches the API, PostgreSQL database, Redis cache, and Celery workers."

### Step 2: Verify Installation

**Screen**: Browser showing API docs

```bash
# Open browser to
http://localhost:8000/docs
```

**Narration**:
> "The API is now running at port 8000. Open the Swagger UI to see interactive documentation for all endpoints."

---

## Part 3: Basic Features (3:00 - 6:00)

### Regex Search

**Screen**: Terminal with Python code

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search/regex",
    json={
        "pattern": r"\d{3}-\d{3}-\d{4}",
        "text": "Contact: 123-456-7890 or 098-765-4321"
    }
)

print(response.json())
# Output: {"matches": ["123-456-7890", "098-765-4321"], ...}
```

**Narration**:
> "Let's start with regex search. Here we're extracting phone numbers using a regex pattern. The API returns all matches instantly."

### Semantic Search

**Screen**: Terminal with semantic search

```python
response = requests.post(
    "http://localhost:8000/api/v1/search/semantic",
    json={
        "query": "machine learning",
        "text": "AI and deep learning transform technology. Neural networks enable pattern recognition.",
        "top_k": 5
    }
)

print(response.json())
```

**Narration**:
> "Now for semantic search. Instead of exact matches, it understands meaning. When we search for 'machine learning', it finds related concepts like 'AI', 'deep learning', and 'neural networks'."

---

## Part 4: Advanced Features (6:00 - 10:00)

### RAG Pipeline

**Screen**: Python code with RAG

```python
from deepgrep.ml import RAGPipeline

# Build knowledge base
pipeline = RAGPipeline()

documents = [
    "Python is great for data science...",
    "Machine learning uses algorithms...",
    "Docker containers package apps..."
]

pipeline.add_documents(documents, chunk_method="sentences")

# Search
results = pipeline.search("How to containerize apps?", k=5)

for text, distance, metadata in results:
    score = 1 / (1 + distance)
    print(f"Score: {score:.3f} - {text}")
```

**Narration**:
> "The RAG pipeline automatically chunks documents, generates embeddings, and stores them in a FAISS vector database for fast similarity search."

### Batch Processing

**Screen**: Show batch processing example

```python
response = requests.post(
    "http://localhost:8000/api/v1/search/batch",
    json={
        "queries": ["error", "warning", "critical"],
        "text": log_content,
        "search_type": "regex"
    }
)
```

**Narration**:
> "Batch processing lets you search for multiple patterns at once, perfect for log analysis."

---

## Part 5: Production Features (10:00 - 13:00)

### Database Integration

**Screen**: Show database schema

**Narration**:
> "DeepGrep uses PostgreSQL for persistence with optimized indexes. All searches are logged with timestamps for analytics."

**Screen**: pgAdmin showing tables

### Caching Layer

**Screen**: Show Redis monitor

**Narration**:
> "Redis caches frequent queries for sub-millisecond response times. Watch how the second identical query is instant."

**Screen**: Terminal showing timing difference

### Background Tasks

**Screen**: Flower dashboard

**Narration**:
> "Celery handles long-running tasks asynchronously. Monitor workers and tasks in real-time with Flower."

**Screen**: http://localhost:5555

---

## Part 6: Metrics & Monitoring (13:00 - 15:00)

### Search Quality Metrics

**Screen**: Python code with metrics

```python
from deepgrep.metrics import SearchMetrics

metrics = SearchMetrics.evaluate_all(
    retrieved={1, 2, 3, 4, 5},
    relevant={2, 3, 4, 5, 6}
)

print(f"Precision: {metrics['precision']:.2f}")
print(f"Recall: {metrics['recall']:.2f}")
print(f"F1 Score: {metrics['f1_score']:.2f}")
```

**Narration**:
> "Built-in metrics help you evaluate search quality with precision, recall, F1 scores, and more."

---

## Part 7: ETL Pipeline (15:00 - 17:00)

### Log Processing

**Screen**: Terminal with ETL code

```python
from deepgrep.etl import ETLPipeline
from deepgrep.database import DatabaseManager

db = DatabaseManager()
pipeline = ETLPipeline(db_manager=db)

result = pipeline.run(
    source_path="/var/log/nginx/",
    log_format="apache",
    output_format="database"
)

print(f"Processed {result['total_entries']} log entries")
```

**Narration**:
> "The ETL pipeline ingests logs from various formats - Apache, Nginx, JSON - parses them, and loads into the database for analysis."

---

## Part 8: Client SDKs (17:00 - 19:00)

### Python SDK

**Screen**: Python code

```python
from deepgrep.sdk.python import DeepGrepClient

client = DeepGrepClient("http://localhost:8000")

# Simple searches
result = client.search_regex(r"\d+", "Found 42 items")
matches = client.search_semantic("happy", text="I feel joyful")
```

**Narration**:
> "Client SDKs make integration easy. Available in Python and JavaScript."

### JavaScript SDK

**Screen**: JavaScript code

```javascript
const { DeepGrepClient } = require('./deepgrep-sdk');

const client = new DeepGrepClient('http://localhost:8000');

const result = await client.searchRegex('\\d+', 'Found 42 items');
const matches = await client.searchSemantic('happy', {
  text: 'I feel joyful'
});
```

---

## Part 9: Deployment (19:00 - 20:00)

### Docker Deployment

**Screen**: Show docker-compose.yml

**Narration**:
> "Deploy everything with Docker Compose - API, database, cache, and workers all configured and ready to go."

### CI/CD Pipeline

**Screen**: Show GitHub Actions workflow

**Narration**:
> "Automated CI/CD with GitHub Actions runs tests, checks code quality, builds Docker images, and deploys."

---

## Part 10: Conclusion (20:00 - 21:00)

**Screen**: Feature summary

**Narration**:
> "DeepGrep combines the best of traditional search and modern AI:
> - Fast regex matching
> - AI-powered semantic search  
> - Production-ready architecture
> - Comprehensive documentation
> - Easy deployment
> 
> Check out the docs at github.com/alwaysvivek/deepgrep
> Star the project if you find it useful!
> Thanks for watching!"

**Screen**: Links to:
- GitHub repo
- Documentation
- API playground
- Community discussions

---

## GIF Walkthrough Alternative

For a quick GIF demo, show:

### GIF 1: API Startup (3 seconds)
```bash
docker-compose up -d
```

### GIF 2: Regex Search (5 seconds)
- Show browser with Swagger UI
- Execute regex search endpoint
- Show results

### GIF 3: Semantic Search (5 seconds)
- Execute semantic search endpoint
- Show similar concepts found

### GIF 4: Batch Processing (5 seconds)
- Upload file
- Process multiple patterns
- Show results

### GIF 5: Monitoring (3 seconds)
- Show Flower dashboard with active tasks
- Show Redis cache stats

---

## Interactive Demo

For hands-on demo, provide:

1. **Sample data**: `demo_data/sample_logs.txt`
2. **Pre-configured searches**: `demo_data/queries.json`
3. **Expected results**: `demo_data/expected_results.json`

Users can run:
```bash
python examples/demo.py
```

This will:
- Start the API if not running
- Load sample data
- Execute all search types
- Show results and metrics
- Clean up

---

## Live Demo Checklist

Before presenting:

- [ ] Services are running (`docker-compose ps`)
- [ ] API is accessible (`curl http://localhost:8000/health`)
- [ ] Sample data is loaded
- [ ] Browser tabs open:
  - API docs: http://localhost:8000/docs
  - Flower: http://localhost:5555
- [ ] Terminal ready with example scripts
- [ ] Network connection stable

During demo:
- [ ] Start with simple regex example
- [ ] Show semantic search capabilities
- [ ] Demonstrate batch processing
- [ ] Show monitoring dashboards
- [ ] Explain architecture diagram
- [ ] Take questions

After demo:
- [ ] Share repository link
- [ ] Provide documentation links
- [ ] Invite to discussions/community

---

## Recording Tips

1. **Resolution**: 1920x1080 minimum
2. **Terminal**: Large font (18pt+), high contrast
3. **Browser**: Zoom to 125-150%
4. **Audio**: Clear microphone, no background noise
5. **Pacing**: Pause between sections
6. **Highlighting**: Use mouse/pointer to highlight important parts

---

## Resources

- Demo repository: https://github.com/alwaysvivek/deepgrep
- Documentation: https://github.com/alwaysvivek/deepgrep/docs
- Live demo: [Add link when deployed]
- Video tutorial: [Add link when created]
