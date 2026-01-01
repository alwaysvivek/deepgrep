"""Async file processing tasks."""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict


async def process_file_async(file_path: str, pattern: str, search_type: str = "regex") -> Dict:
    """
    Process file asynchronously.

    Args:
        file_path: Path to file
        pattern: Search pattern or query
        search_type: 'regex' or 'semantic'

    Returns:
        Dictionary with results
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()

        if search_type == "regex":
            from deepgrep.core.engine import find_matches
            matches = []
            for line in content.splitlines():
                line_matches = find_matches(line, pattern)
                matches.extend(line_matches)

            return {
                "file": file_path,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
        else:  # semantic
            from deepgrep.ml import RAGPipeline
            pipeline = RAGPipeline()
            pipeline.add_documents([content], chunk_method="sentences")
            results = pipeline.search(pattern, k=10)

            matches = [
                {"text": text, "score": 1.0 / (1.0 + distance)}
                for text, distance, _ in results
            ]

            return {
                "file": file_path,
                "query": pattern,
                "matches": matches,
                "count": len(matches)
            }
    except Exception as e:
        return {"error": str(e), "file": file_path}


async def process_files_batch(file_paths: List[str], pattern: str, search_type: str = "regex") -> List[Dict]:
    """
    Process multiple files concurrently.

    Args:
        file_paths: List of file paths
        pattern: Search pattern or query
        search_type: 'regex' or 'semantic'

    Returns:
        List of results
    """
    tasks = [process_file_async(fp, pattern, search_type) for fp in file_paths]
    results = await asyncio.gather(*tasks)
    return results
