"""DeepGrep Python SDK - Client library for DeepGrep API."""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Result from a search operation."""
    matches: List[str]
    count: int
    pattern: Optional[str] = None
    query: Optional[str] = None


@dataclass
class SemanticMatch:
    """A single semantic search match."""
    text: str
    score: float
    metadata: Dict[str, Any]


class DeepGrepClient:
    """Client for interacting with DeepGrep API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize DeepGrep client.

        Args:
            base_url: Base URL of the DeepGrep API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def search_regex(self, pattern: str, text: str) -> SearchResult:
        """
        Perform regex pattern search.

        Args:
            pattern: Regex pattern to search for
            text: Text to search in

        Returns:
            SearchResult with matches

        Raises:
            requests.HTTPError: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/search/regex",
            json={"pattern": pattern, "text": text}
        )
        response.raise_for_status()
        data = response.json()

        return SearchResult(
            matches=data["matches"],
            count=data["count"],
            pattern=data["pattern"]
        )

    def search_semantic(
        self,
        query: str,
        text: Optional[str] = None,
        documents: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[SemanticMatch]:
        """
        Perform semantic search.

        Args:
            query: Search query
            text: Single text to search (optional)
            documents: Multiple documents to search (optional)
            top_k: Number of results to return

        Returns:
            List of SemanticMatch objects

        Raises:
            ValueError: If neither text nor documents provided
            requests.HTTPError: If the request fails
        """
        if text is None and documents is None:
            raise ValueError("Either text or documents must be provided")

        payload = {"query": query, "top_k": top_k}
        if text:
            payload["text"] = text
        if documents:
            payload["documents"] = documents

        response = self.session.post(
            f"{self.base_url}/api/v1/search/semantic",
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        return [
            SemanticMatch(
                text=match["text"],
                score=match["score"],
                metadata=match.get("metadata", {})
            )
            for match in data["matches"]
        ]

    def batch_search(
        self,
        queries: List[str],
        text: str,
        search_type: str = "regex"
    ) -> List[Dict[str, Any]]:
        """
        Perform batch search with multiple queries.

        Args:
            queries: List of search queries
            text: Text to search in
            search_type: Type of search ('regex' or 'semantic')

        Returns:
            List of results for each query

        Raises:
            requests.HTTPError: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/search/batch",
            json={
                "queries": queries,
                "text": text,
                "search_type": search_type
            }
        )
        response.raise_for_status()
        data = response.json()

        return data["results"]

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a file for processing.

        Args:
            file_path: Path to file to upload

        Returns:
            Upload result information

        Raises:
            requests.HTTPError: If the request fails
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/api/v1/upload",
                files=files
            )
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get search history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of history entries

        Raises:
            requests.HTTPError: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/api/v1/history",
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()

        return data["history"]

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health.

        Returns:
            Health status information

        Raises:
            requests.HTTPError: If the request fails
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


# Convenience functions
def search_regex(pattern: str, text: str, base_url: str = "http://localhost:8000") -> SearchResult:
    """Quick regex search without creating a client."""
    client = DeepGrepClient(base_url)
    return client.search_regex(pattern, text)


def search_semantic(
    query: str,
    text: str,
    base_url: str = "http://localhost:8000",
    top_k: int = 10
) -> List[SemanticMatch]:
    """Quick semantic search without creating a client."""
    client = DeepGrepClient(base_url)
    return client.search_semantic(query, text=text, top_k=top_k)
