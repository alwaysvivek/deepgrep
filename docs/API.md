# 🔌 DeepGrep API Reference

Complete API documentation for DeepGrep v2.0.

---

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API doesn't require authentication. Future versions will support API keys.

---

## Endpoints

### Health Check

#### `GET /`

Root endpoint health check.

**Response**

```json
{
  "status": "healthy",
  "message": "DeepGrep API is running",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### `GET /health`

Detailed health status.

**Response**

```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

### Regex Search

#### `POST /api/v1/search/regex`

Perform regex pattern matching.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pattern | string | Yes | Regex pattern |
| text | string | Yes | Text to search |

**Example Request**

```json
{
  "pattern": "\\d{3}-\\d{3}-\\d{4}",
  "text": "Call 123-456-7890 or 098-765-4321"
}
```

**Response**

```json
{
  "matches": ["123-456-7890", "098-765-4321"],
  "count": 2,
  "pattern": "\\d{3}-\\d{3}-\\d{4}"
}
```

**Status Codes**

- `200`: Success
- `400`: Invalid request
- `422`: Validation error
- `500`: Server error

---

### Semantic Search

#### `POST /api/v1/search/semantic`

Perform AI-powered semantic search.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | Search query |
| text | string | No* | Single text to search |
| documents | array[string] | No* | Multiple documents |
| top_k | integer | No | Results to return (default: 10) |

\* Either `text` or `documents` must be provided

**Example Request**

```json
{
  "query": "machine learning algorithms",
  "text": "Deep learning uses neural networks. Random forests are ensemble methods. Support vector machines classify data.",
  "top_k": 3
}
```

**Response**

```json
{
  "matches": [
    {
      "text": "Deep learning uses neural networks.",
      "score": 0.892,
      "metadata": {
        "doc_id": 0,
        "chunk_id": 0,
        "total_chunks": 3
      }
    },
    {
      "text": "Random forests are ensemble methods.",
      "score": 0.785,
      "metadata": {
        "doc_id": 0,
        "chunk_id": 1,
        "total_chunks": 3
      }
    }
  ],
  "count": 2,
  "query": "machine learning algorithms"
}
```

**Status Codes**

- `200`: Success
- `400`: Invalid request (no text/documents)
- `422`: Validation error
- `500`: Server error

---

### Batch Search

#### `POST /api/v1/search/batch`

Process multiple search queries at once.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| queries | array[string] | Yes | List of queries |
| text | string | Yes | Text to search |
| search_type | string | No | "regex" or "semantic" (default: "regex") |

**Example Request**

```json
{
  "queries": ["error", "warning", "info"],
  "text": "2024-01-01 ERROR: Failed\n2024-01-01 INFO: Started\n2024-01-01 WARNING: Slow",
  "search_type": "regex"
}
```

**Response**

```json
{
  "results": [
    {
      "query": "error",
      "matches": ["ERROR"],
      "count": 1
    },
    {
      "query": "warning",
      "matches": ["WARNING"],
      "count": 1
    },
    {
      "query": "info",
      "matches": ["INFO"],
      "count": 1
    }
  ],
  "total_queries": 3
}
```

**Status Codes**

- `200`: Success
- `422`: Validation error
- `500`: Server error

---

### File Upload

#### `POST /api/v1/upload`

Upload a file for processing.

**Request**

- Content-Type: `multipart/form-data`
- Form field: `file`

**Example (curl)**

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.txt"
```

**Response**

```json
{
  "status": "uploaded",
  "filename": "document.txt",
  "size": 1024,
  "path": "uploads/document.txt"
}
```

**Status Codes**

- `200`: Success
- `400`: No file provided
- `500`: Upload failed

---

### Search History

#### `GET /api/v1/history`

Retrieve search history.

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 50 | Max entries to return |

**Example Request**

```
GET /api/v1/history?limit=10
```

**Response**

```json
{
  "history": [
    {
      "pattern": "\\d+",
      "timestamp": "2024-01-01T12:00:00",
      "matches_count": 5
    },
    {
      "pattern": "error",
      "timestamp": "2024-01-01T11:55:00",
      "matches_count": 2
    }
  ],
  "count": 2
}
```

**Status Codes**

- `200`: Success
- `500`: Server error

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 422 | Validation Error - Request doesn't match schema |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting. Future versions may implement:
- 100 requests/minute per IP
- 1000 requests/hour per API key

---

## Examples

### Python

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

### JavaScript

```javascript
// Regex search
const response = await fetch('http://localhost:8000/api/v1/search/regex', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    pattern: '\\d+',
    text: 'Found 42 items'
  })
});
const data = await response.json();
console.log(data);
```

### cURL

```bash
# Regex search
curl -X POST http://localhost:8000/api/v1/search/regex \
  -H "Content-Type: application/json" \
  -d '{"pattern": "\\d+", "text": "Found 42 items"}'

# Semantic search
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "happy", "text": "I feel joyful", "top_k": 5}'
```

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation with:
- Try out endpoints directly
- See request/response schemas
- View all parameters and descriptions
- Test authentication

Alternative documentation at http://localhost:8000/redoc

---

## SDK Usage

### Python SDK

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

### JavaScript SDK

```javascript
const { DeepGrepClient } = require('./deepgrep-sdk');

const client = new DeepGrepClient('http://localhost:8000');

// Regex search
const result = await client.searchRegex('\\d+', 'Found 42 items');
console.log(result.matches);

// Semantic search
const matches = await client.searchSemantic('happy', {
  text: 'I feel joyful',
  topK: 5
});
matches.matches.forEach(m => console.log(`${m.score}: ${m.text}`));
```

---

## Changelog

### v2.0.0 (2024-01-01)

**Added**
- Semantic search with sentence transformers
- FAISS vector store integration
- RAG pipeline with document chunking
- Batch search endpoint
- File upload endpoint
- Search history endpoint
- Comprehensive metrics
- Redis caching
- PostgreSQL support
- Celery background tasks

**Changed**
- Migrated from Flask to FastAPI
- Async endpoint support
- Improved error handling

**Deprecated**
- Legacy `/search` endpoint (use `/api/v1/search/regex`)
- Legacy `/semantic` endpoint (use `/api/v1/search/semantic`)

---

## Support

- **Documentation**: https://github.com/alwaysvivek/deepgrep/docs
- **Issues**: https://github.com/alwaysvivek/deepgrep/issues
- **Discussions**: https://github.com/alwaysvivek/deepgrep/discussions
