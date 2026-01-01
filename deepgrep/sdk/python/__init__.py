"""Python SDK for DeepGrep."""

from .client import DeepGrepClient, SearchResult, SemanticMatch, search_regex, search_semantic

__version__ = "2.0.0"
__all__ = [
    "DeepGrepClient",
    "SearchResult",
    "SemanticMatch",
    "search_regex",
    "search_semantic"
]
