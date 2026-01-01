"""
Example 3: API Client Usage

Demonstrates using the DeepGrep API with the Python SDK.
"""

import sys
import requests
from deepgrep.sdk.python import DeepGrepClient


def check_api_health(base_url: str = "http://localhost:8000"):
    """Check if API is running."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        print("✓ API is running")
        return True
    except Exception as e:
        print(f"✗ API is not available: {e}")
        print("Please start the API with: uvicorn deepgrep.api.main:app")
        return False


def regex_search_example(client: DeepGrepClient):
    """Example of regex search."""
    print("\n" + "=" * 80)
    print("Example 1: Regex Search")
    print("=" * 80)
    
    text = """
    Error on line 42: FileNotFoundError
    Warning on line 67: DeprecationWarning
    Success on line 89: Operation completed
    Error on line 103: ValueError
    """
    
    # Search for errors
    result = client.search_regex(r"Error.*line \d+", text)
    
    print(f"\nPattern: Error.*line \\d+")
    print(f"Found {result.count} matches:")
    for match in result.matches:
        print(f"  - {match}")


def semantic_search_example(client: DeepGrepClient):
    """Example of semantic search."""
    print("\n" + "=" * 80)
    print("Example 2: Semantic Search")
    print("=" * 80)
    
    text = """
    Machine learning algorithms can recognize patterns in data.
    Neural networks are inspired by biological neurons.
    Deep learning uses multiple layers to extract features.
    Random forests combine many decision trees.
    Support vector machines find optimal hyperplanes.
    """
    
    query = "artificial intelligence techniques"
    matches = client.search_semantic(query, text=text, top_k=3)
    
    print(f"\nQuery: {query}")
    print(f"Found {len(matches)} relevant chunks:")
    
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. Score: {match.score:.3f}")
        print(f"   Text: {match.text.strip()}")


def batch_search_example(client: DeepGrepClient):
    """Example of batch search."""
    print("\n" + "=" * 80)
    print("Example 3: Batch Search")
    print("=" * 80)
    
    log_text = """
    2024-01-01 10:00:00 INFO Application started
    2024-01-01 10:01:15 ERROR Database connection failed
    2024-01-01 10:01:30 WARNING Retrying connection
    2024-01-01 10:02:00 INFO Connection established
    2024-01-01 10:05:00 ERROR Query timeout
    2024-01-01 10:06:00 INFO Request completed
    """
    
    queries = ["ERROR", "WARNING", "INFO"]
    results = client.batch_search(queries, log_text, search_type="regex")
    
    print("\nBatch search results:")
    for result in results:
        print(f"\nQuery: {result['query']}")
        print(f"Matches: {result['count']}")
        for match in result['matches'][:3]:  # Show first 3
            print(f"  - {match}")


def history_example(client: DeepGrepClient):
    """Example of getting search history."""
    print("\n" + "=" * 80)
    print("Example 4: Search History")
    print("=" * 80)
    
    history = client.get_history(limit=5)
    
    print(f"\nRecent searches (showing {len(history)} entries):")
    for entry in history:
        print(f"\n- Pattern: {entry['pattern']}")
        print(f"  Time: {entry['timestamp']}")
        print(f"  Matches: {entry['matches_count']}")


if __name__ == "__main__":
    base_url = "http://localhost:8000"
    
    # Check API health
    if not check_api_health(base_url):
        sys.exit(1)
    
    # Create client
    client = DeepGrepClient(base_url)
    
    # Run examples
    try:
        regex_search_example(client)
        semantic_search_example(client)
        batch_search_example(client)
        history_example(client)
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        sys.exit(1)
