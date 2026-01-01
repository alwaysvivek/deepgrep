"""Celery tasks for background processing."""

import os
from celery import Celery

# Initialize Celery
celery_app = Celery(
    "deepgrep",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="deepgrep.tasks.process_file")
def process_file_task(file_path: str, pattern: str, search_type: str = "regex"):
    """
    Process a file with the given pattern asynchronously.

    Args:
        file_path: Path to the file to process
        pattern: Search pattern or query
        search_type: Type of search ('regex' or 'semantic')

    Returns:
        Dictionary with results
    """
    try:
        from pathlib import Path
        from deepgrep.core.engine import find_matches
        from deepgrep.ml import RAGPipeline

        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if search_type == "regex":
            matches = []
            for line in content.splitlines():
                line_matches = find_matches(line, pattern)
                matches.extend(line_matches)

            return {
                "file": str(file_path),
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
        else:  # semantic
            pipeline = RAGPipeline()
            pipeline.add_documents([content], chunk_method="sentences")
            results = pipeline.search(pattern, k=10)

            matches = [
                {"text": text, "score": 1.0 / (1.0 + distance)}
                for text, distance, _ in results
            ]

            return {
                "file": str(file_path),
                "query": pattern,
                "matches": matches,
                "count": len(matches)
            }
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name="deepgrep.tasks.batch_process")
def batch_process_task(file_paths: list, pattern: str, search_type: str = "regex"):
    """
    Process multiple files in batch.

    Args:
        file_paths: List of file paths to process
        pattern: Search pattern or query
        search_type: Type of search ('regex' or 'semantic')

    Returns:
        Dictionary with batch results
    """
    results = []
    for file_path in file_paths:
        result = process_file_task(file_path, pattern, search_type)
        results.append(result)

    return {
        "total_files": len(file_paths),
        "results": results
    }


@celery_app.task(name="deepgrep.tasks.index_documents")
def index_documents_task(documents: list, save_path: str = None):
    """
    Index documents for semantic search.

    Args:
        documents: List of document texts
        save_path: Optional path to save the index

    Returns:
        Dictionary with indexing results
    """
    try:
        from deepgrep.ml import RAGPipeline

        pipeline = RAGPipeline()
        pipeline.add_documents(documents, chunk_method="sentences")

        if save_path:
            pipeline.save(save_path)

        return {
            "status": "success",
            "documents_indexed": len(documents),
            "save_path": save_path
        }
    except Exception as e:
        return {"error": str(e)}
