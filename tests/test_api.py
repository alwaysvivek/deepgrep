"""Tests for FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from deepgrep.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRegexSearch:
    """Test regex search endpoints."""

    def test_regex_search_success(self, client):
        """Test successful regex search."""
        response = client.post(
            "/api/v1/search/regex",
            json={
                "pattern": r"\d+",
                "text": "Found 42 items and 17 users"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "count" in data
        assert data["count"] == len(data["matches"])

    def test_regex_search_invalid_pattern(self, client):
        """Test regex search with invalid pattern."""
        response = client.post(
            "/api/v1/search/regex",
            json={
                "pattern": "",
                "text": "test"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_regex_search_missing_field(self, client):
        """Test regex search with missing field."""
        response = client.post(
            "/api/v1/search/regex",
            json={
                "pattern": r"\d+"
            }
        )
        assert response.status_code == 422


class TestSemanticSearch:
    """Test semantic search endpoints."""

    def test_semantic_search_success(self, client):
        """Test successful semantic search."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "happy",
                "text": "I feel joyful and delighted today",
                "top_k": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "count" in data
        assert "query" in data

    def test_semantic_search_missing_text(self, client):
        """Test semantic search without text or documents."""
        response = client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test"
            }
        )
        assert response.status_code == 400


class TestBatchSearch:
    """Test batch search endpoints."""

    def test_batch_regex_search(self, client):
        """Test batch regex search."""
        response = client.post(
            "/api/v1/search/batch",
            json={
                "queries": ["\\d+", "[a-z]+"],
                "text": "Test 123 data 456",
                "search_type": "regex"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_queries" in data
        assert data["total_queries"] == 2


class TestHistory:
    """Test history endpoints."""

    def test_get_history(self, client):
        """Test getting search history."""
        response = client.get("/api/v1/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "count" in data
