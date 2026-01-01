"""FastAPI application with async endpoints."""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
import aiofiles
from pathlib import Path

from .models import (
    SearchRequest,
    SearchResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    BatchSearchRequest,
    BatchSearchResponse,
    HealthResponse
)
from .dependencies import (
    get_embedding_engine,
    get_vector_store,
    get_cache,
    get_db
)
from deepgrep.core.engine import find_matches
from deepgrep.ml import RAGPipeline
from deepgrep.tasks.search_tasks import process_file_async

# Create FastAPI app
app = FastAPI(
    title="DeepGrep API",
    description="Lightning-fast regex meets AI-powered semantic search",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag_pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    global rag_pipeline
    rag_pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")
    print("DeepGrep API started successfully")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="DeepGrep API is running"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )


@app.post("/api/v1/search/regex", response_model=SearchResponse)
async def search_regex(request: SearchRequest):
    """
    Perform regex pattern matching.

    Args:
        request: Search request with pattern and text

    Returns:
        Search results with matches
    """
    try:
        matches = []
        for line in request.text.splitlines():
            line_matches = find_matches(line, request.pattern)
            matches.extend(line_matches)

        return SearchResponse(
            matches=matches,
            count=len(matches),
            pattern=request.pattern
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/search/semantic", response_model=SemanticSearchResponse)
async def search_semantic(request: SemanticSearchRequest):
    """
    Perform semantic search using embeddings.

    Args:
        request: Semantic search request with query and text/documents

    Returns:
        Semantic search results with similarity scores
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG pipeline not initialized")

        # Add documents to the pipeline
        documents = [request.text] if request.text else request.documents
        if not documents:
            raise HTTPException(status_code=400, detail="No text or documents provided")

        # Create a temporary pipeline for this request
        temp_pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")
        temp_pipeline.add_documents(documents, chunk_method="sentences")

        # Search
        results = temp_pipeline.search(request.query, k=request.top_k or 10)

        matches = [
            {
                "text": text,
                "score": float(1.0 / (1.0 + distance)),  # Convert distance to similarity
                "metadata": metadata
            }
            for text, distance, metadata in results
        ]

        return SemanticSearchResponse(
            matches=matches,
            count=len(matches),
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search/batch", response_model=BatchSearchResponse)
async def batch_search(request: BatchSearchRequest, background_tasks: BackgroundTasks):
    """
    Process batch search requests asynchronously.

    Args:
        request: Batch search request with multiple queries
        background_tasks: FastAPI background tasks

    Returns:
        Batch results with job ID
    """
    try:
        results = []

        for query in request.queries:
            if request.search_type == "regex":
                matches = []
                for line in request.text.splitlines():
                    line_matches = find_matches(line, query)
                    matches.extend(line_matches)
                results.append({
                    "query": query,
                    "matches": matches,
                    "count": len(matches)
                })
            else:  # semantic
                temp_pipeline = RAGPipeline(embedding_model="all-MiniLM-L6-v2")
                temp_pipeline.add_documents([request.text], chunk_method="sentences")
                search_results = temp_pipeline.search(query, k=10)

                matches = [
                    {
                        "text": text,
                        "score": float(1.0 / (1.0 + distance))
                    }
                    for text, distance, _ in search_results
                ]
                results.append({
                    "query": query,
                    "matches": matches,
                    "count": len(matches)
                })

        return BatchSearchResponse(
            results=results,
            total_queries=len(request.queries)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload and process file asynchronously.

    Args:
        file: Uploaded file
        background_tasks: FastAPI background tasks

    Returns:
        Upload status and file ID
    """
    try:
        # Save file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        return {
            "status": "uploaded",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history")
async def get_history(limit: int = 50):
    """
    Get search history.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        List of search history entries
    """
    try:
        from deepgrep.core.history import SearchHistoryDB
        history_db = SearchHistoryDB()
        all_history = history_db.list_all(limit=limit)

        return {
            "history": [
                {
                    "pattern": r[0],
                    "timestamp": r[1],
                    "matches_count": r[2]
                }
                for r in all_history
            ],
            "count": len(all_history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
