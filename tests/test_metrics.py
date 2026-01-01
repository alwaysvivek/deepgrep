"""Tests for metrics module."""

import pytest
from deepgrep.metrics import SearchMetrics


class TestPrecisionRecallF1:
    """Test basic precision, recall, and F1 metrics."""

    def test_perfect_match(self):
        """Test with perfect match."""
        retrieved = {1, 2, 3, 4, 5}
        relevant = {1, 2, 3, 4, 5}

        assert SearchMetrics.precision(retrieved, relevant) == 1.0
        assert SearchMetrics.recall(retrieved, relevant) == 1.0
        assert SearchMetrics.f1_score(retrieved, relevant) == 1.0

    def test_partial_match(self):
        """Test with partial match."""
        retrieved = {1, 2, 3, 4}
        relevant = {3, 4, 5, 6}

        precision = SearchMetrics.precision(retrieved, relevant)
        recall = SearchMetrics.recall(retrieved, relevant)
        f1 = SearchMetrics.f1_score(retrieved, relevant)

        assert precision == 0.5  # 2 out of 4 retrieved are relevant
        assert recall == 0.5     # 2 out of 4 relevant are retrieved
        assert f1 == 0.5

    def test_no_match(self):
        """Test with no matches."""
        retrieved = {1, 2, 3}
        relevant = {4, 5, 6}

        assert SearchMetrics.precision(retrieved, relevant) == 0.0
        assert SearchMetrics.recall(retrieved, relevant) == 0.0
        assert SearchMetrics.f1_score(retrieved, relevant) == 0.0

    def test_empty_retrieved(self):
        """Test with empty retrieved set."""
        retrieved = set()
        relevant = {1, 2, 3}

        assert SearchMetrics.precision(retrieved, relevant) == 0.0
        assert SearchMetrics.recall(retrieved, relevant) == 0.0
        assert SearchMetrics.f1_score(retrieved, relevant) == 0.0


class TestAveragePrecision:
    """Test average precision metrics."""

    def test_average_precision(self):
        """Test AP calculation."""
        retrieved_ranked = [1, 2, 3, 4, 5]
        relevant = {2, 3, 5}

        ap = SearchMetrics.average_precision(retrieved_ranked, relevant)
        assert ap > 0.0
        assert ap <= 1.0

    def test_map(self):
        """Test MAP calculation."""
        queries_results = [
            ([1, 2, 3], {2, 3}),
            ([4, 5, 6], {5, 6}),
        ]

        map_score = SearchMetrics.mean_average_precision(queries_results)
        assert map_score > 0.0
        assert map_score <= 1.0


class TestNDCG:
    """Test NDCG metric."""

    def test_ndcg_perfect(self):
        """Test NDCG with perfect ranking."""
        retrieved_ranked = [1, 2, 3, 4, 5]
        relevance_scores = {1: 3, 2: 2, 3: 1, 4: 0, 5: 0}

        ndcg = SearchMetrics.ndcg(retrieved_ranked, relevance_scores, k=5)
        assert ndcg == 1.0

    def test_ndcg_partial(self):
        """Test NDCG with non-optimal ranking."""
        retrieved_ranked = [5, 4, 3, 2, 1]  # Reverse order
        relevance_scores = {1: 3, 2: 2, 3: 1, 4: 0, 5: 0}

        ndcg = SearchMetrics.ndcg(retrieved_ranked, relevance_scores, k=5)
        assert 0.0 <= ndcg < 1.0


class TestMRR:
    """Test Mean Reciprocal Rank."""

    def test_mrr(self):
        """Test MRR calculation."""
        queries_results = [
            ([1, 2, 3], {2}),  # First relevant at position 2
            ([4, 5, 6], {4}),  # First relevant at position 1
        ]

        mrr = SearchMetrics.mrr(queries_results)
        expected = (1/2 + 1/1) / 2  # Average of 0.5 and 1.0
        assert abs(mrr - expected) < 0.01


class TestEvaluateAll:
    """Test combined evaluation."""

    def test_evaluate_all(self):
        """Test evaluating all metrics at once."""
        retrieved = {1, 2, 3, 4, 5}
        relevant = {3, 4, 5, 6, 7}

        metrics = SearchMetrics.evaluate_all(retrieved, relevant)

        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1_score"] <= 1.0
