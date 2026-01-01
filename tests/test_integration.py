"""Basic integration test to verify the installation is working."""

import pytest
from deepgrep.core.engine import find_matches
from deepgrep.metrics import SearchMetrics


def test_basic_regex():
    """Test basic regex functionality."""
    line = "Found 42 items and 17 users"
    pattern = r"\d+"
    matches = find_matches(line, pattern)
    assert matches == ["42", "17"]


def test_word_extraction():
    """Test word extraction."""
    line = "hello world test data"
    pattern = r"\w+"
    matches = find_matches(line, pattern)
    assert len(matches) == 4
    assert "hello" in matches
    assert "world" in matches


def test_metrics():
    """Test metrics calculations."""
    retrieved = {1, 2, 3, 4}
    relevant = {2, 3, 4, 5}
    
    metrics = SearchMetrics.evaluate_all(retrieved, relevant)
    
    assert metrics["precision"] == 0.75  # 3 out of 4
    assert metrics["recall"] == 0.75     # 3 out of 4
    assert metrics["f1_score"] == 0.75


def test_etl_log_parser():
    """Test ETL log parser."""
    from deepgrep.etl import LogParser
    
    # Test generic log parsing
    log_line = "2024-01-01 10:00:00 ERROR Something went wrong"
    result = LogParser.parse_generic_log(log_line)
    
    assert result is not None
    assert result["level"] == "ERROR"
    assert "timestamp" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
