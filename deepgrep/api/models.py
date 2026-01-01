"""Pydantic models for API validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchRequest(BaseModel):
    """Request model for regex search."""
    pattern: str = Field(..., description="Regex pattern to search for")
    text: str = Field(..., description="Text to search in")

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v):
        if not v or not v.strip():
            raise ValueError("Pattern cannot be empty")
        return v


class SearchResponse(BaseModel):
    """Response model for regex search."""
    matches: List[str] = Field(default_factory=list, description="List of matches found")
    count: int = Field(..., description="Number of matches")
    pattern: str = Field(..., description="Pattern used for search")


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., description="Search query")
    text: Optional[str] = Field(None, description="Single text to search in")
    documents: Optional[List[str]] = Field(None, description="Multiple documents to search")
    top_k: Optional[int] = Field(10, ge=1, le=100, description="Number of results to return")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v


class SemanticMatch(BaseModel):
    """Model for a semantic search match."""
    text: str = Field(..., description="Matched text")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search."""
    matches: List[Dict[str, Any]] = Field(default_factory=list, description="List of semantic matches")
    count: int = Field(..., description="Number of matches")
    query: str = Field(..., description="Query used for search")


class BatchSearchRequest(BaseModel):
    """Request model for batch search."""
    queries: List[str] = Field(..., min_length=1, description="List of queries")
    text: str = Field(..., description="Text to search in")
    search_type: str = Field("regex", description="Type of search: 'regex' or 'semantic'")

    @field_validator('search_type')
    @classmethod
    def validate_search_type(cls, v):
        if v not in ["regex", "semantic"]:
            raise ValueError("search_type must be 'regex' or 'semantic'")
        return v


class BatchSearchResponse(BaseModel):
    """Response model for batch search."""
    results: List[Dict[str, Any]] = Field(default_factory=list, description="List of search results")
    total_queries: int = Field(..., description="Total number of queries processed")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HistoryEntry(BaseModel):
    """Model for a search history entry."""
    pattern: str = Field(..., description="Search pattern or query")
    timestamp: str = Field(..., description="Search timestamp")
    matches_count: int = Field(..., description="Number of matches found")


class DocumentChunk(BaseModel):
    """Model for a document chunk in RAG pipeline."""
    text: str = Field(..., description="Chunk text")
    doc_id: int = Field(..., description="Parent document ID")
    chunk_id: int = Field(..., description="Chunk ID within document")
    total_chunks: int = Field(..., description="Total chunks in parent document")


class ETLJobRequest(BaseModel):
    """Request model for ETL job."""
    source_path: str = Field(..., description="Path to source file or directory")
    job_type: str = Field("log_ingestion", description="Type of ETL job")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional options")


class ETLJobResponse(BaseModel):
    """Response model for ETL job."""
    job_id: str = Field(..., description="Unique job ID")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation time")
