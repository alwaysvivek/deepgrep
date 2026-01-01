"""ETL pipeline for log file ingestion."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from datetime import datetime
import json


class LogParser:
    """Parse various log formats."""

    @staticmethod
    def parse_apache_log(line: str) -> Optional[Dict[str, Any]]:
        """Parse Apache/Nginx access log format."""
        pattern = r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<path>[^\s]+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<size>\d+)'
        match = re.match(pattern, line)
        if match:
            return match.groupdict()
        return None

    @staticmethod
    def parse_json_log(line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON-formatted logs."""
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def parse_generic_log(line: str) -> Dict[str, Any]:
        """Parse generic log format with timestamp extraction."""
        # Try to extract timestamp
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            r'\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}',
        ]

        timestamp = None
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp = match.group(0)
                break

        # Try to extract log level
        level_pattern = r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)\b'
        level_match = re.search(level_pattern, line, re.IGNORECASE)
        level = level_match.group(1).upper() if level_match else "UNKNOWN"

        return {
            "timestamp": timestamp,
            "level": level,
            "message": line.strip(),
            "raw": line
        }


class ETLPipeline:
    """ETL pipeline for log file processing."""

    def __init__(self, db_manager=None):
        """
        Initialize ETL pipeline.

        Args:
            db_manager: Optional database manager for storing results
        """
        self.db_manager = db_manager
        self.parser = LogParser()

    def extract(self, source_path: str, file_pattern: str = "*.log") -> List[str]:
        """
        Extract log files from source.

        Args:
            source_path: Path to log file or directory
            file_pattern: Pattern for matching log files

        Returns:
            List of file paths
        """
        path = Path(source_path)
        if path.is_file():
            return [str(path)]
        elif path.is_dir():
            return [str(f) for f in path.glob(file_pattern)]
        else:
            raise ValueError(f"Invalid source path: {source_path}")

    def transform(
        self,
        file_path: str,
        log_format: str = "generic"
    ) -> List[Dict[str, Any]]:
        """
        Transform log file into structured data.

        Args:
            file_path: Path to log file
            log_format: Log format ('apache', 'json', or 'generic')

        Returns:
            List of parsed log entries
        """
        parsed_logs = []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Parse based on format
                if log_format == "apache":
                    parsed = self.parser.parse_apache_log(line)
                elif log_format == "json":
                    parsed = self.parser.parse_json_log(line)
                else:
                    parsed = self.parser.parse_generic_log(line)

                if parsed:
                    parsed["source_file"] = file_path
                    parsed["line_number"] = line_num
                    parsed_logs.append(parsed)

        return parsed_logs

    def load(self, data: List[Dict[str, Any]], output_format: str = "json") -> str:
        """
        Load transformed data.

        Args:
            data: Transformed log data
            output_format: Output format ('json', 'database', or 'both')

        Returns:
            Status message
        """
        if output_format in ["json", "both"]:
            output_path = Path("output") / f"processed_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path.parent.mkdir(exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

        if output_format in ["database", "both"] and self.db_manager:
            for entry in data:
                self.db_manager.add_document(
                    content=entry.get("message", ""),
                    title=f"Log: {entry.get('source_file', 'unknown')}",
                    source=entry.get("source_file"),
                    metadata=entry
                )

        return f"Loaded {len(data)} log entries"

    def run(
        self,
        source_path: str,
        log_format: str = "generic",
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Run complete ETL pipeline.

        Args:
            source_path: Path to log file or directory
            log_format: Log format type
            output_format: Output format

        Returns:
            Pipeline execution summary
        """
        # Extract
        files = self.extract(source_path)

        # Transform and Load
        total_entries = 0
        processed_files = []

        for file_path in files:
            try:
                data = self.transform(file_path, log_format)
                self.load(data, output_format)
                total_entries += len(data)
                processed_files.append(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return {
            "status": "completed",
            "files_processed": len(processed_files),
            "total_entries": total_entries,
            "files": processed_files
        }


class BatchProcessor:
    """Batch processing for large datasets."""

    @staticmethod
    def process_in_batches(
        items: List[Any],
        batch_size: int = 1000,
        processor_func=None
    ) -> List[Any]:
        """
        Process items in batches.

        Args:
            items: List of items to process
            batch_size: Number of items per batch
            processor_func: Function to process each batch

        Returns:
            List of processed results
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            if processor_func:
                batch_result = processor_func(batch)
                results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
            else:
                results.extend(batch)
        return results
