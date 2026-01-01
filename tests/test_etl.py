"""Tests for ETL pipeline."""

import pytest
import tempfile
from pathlib import Path
from deepgrep.etl import ETLPipeline, LogParser, BatchProcessor


class TestLogParser:
    """Test log parsing functionality."""

    def test_parse_apache_log(self):
        """Test Apache log parsing."""
        line = '127.0.0.1 - - [01/Jan/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234'
        result = LogParser.parse_apache_log(line)

        assert result is not None
        assert result["ip"] == "127.0.0.1"
        assert result["method"] == "GET"
        assert result["status"] == "200"

    def test_parse_json_log(self):
        """Test JSON log parsing."""
        line = '{"timestamp": "2024-01-01T10:00:00", "level": "INFO", "message": "Test"}'
        result = LogParser.parse_json_log(line)

        assert result is not None
        assert result["level"] == "INFO"
        assert result["message"] == "Test"

    def test_parse_generic_log(self):
        """Test generic log parsing."""
        line = "2024-01-01 10:00:00 ERROR Something went wrong"
        result = LogParser.parse_generic_log(line)

        assert result is not None
        assert result["level"] == "ERROR"
        assert "timestamp" in result


class TestETLPipeline:
    """Test ETL pipeline."""

    def test_extract_single_file(self):
        """Test extracting a single file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("test log line\n")
            temp_path = f.name

        try:
            pipeline = ETLPipeline()
            files = pipeline.extract(temp_path)
            assert len(files) == 1
            assert files[0] == temp_path
        finally:
            Path(temp_path).unlink()

    def test_transform(self):
        """Test transforming log data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2024-01-01 10:00:00 INFO Test log\n")
            f.write("2024-01-01 10:00:01 ERROR Error log\n")
            temp_path = f.name

        try:
            pipeline = ETLPipeline()
            data = pipeline.transform(temp_path, log_format="generic")

            assert len(data) == 2
            assert all("level" in entry for entry in data)
            assert any(entry["level"] == "ERROR" for entry in data)
        finally:
            Path(temp_path).unlink()


class TestBatchProcessor:
    """Test batch processing."""

    def test_process_in_batches(self):
        """Test batch processing."""
        items = list(range(100))

        def processor(batch):
            return [x * 2 for x in batch]

        results = BatchProcessor.process_in_batches(
            items,
            batch_size=10,
            processor_func=processor
        )

        assert len(results) == 100
        assert results[0] == 0
        assert results[50] == 100
