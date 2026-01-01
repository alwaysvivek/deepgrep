"""Metrics module for evaluating search quality."""

from typing import List, Set, Dict, Tuple
import numpy as np


class SearchMetrics:
    """Calculate precision, recall, and F1 scores for search quality."""

    @staticmethod
    def precision(retrieved: Set, relevant: Set) -> float:
        """
        Calculate precision: fraction of retrieved documents that are relevant.

        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs

        Returns:
            Precision score between 0 and 1
        """
        if not retrieved:
            return 0.0

        true_positives = len(retrieved & relevant)
        return true_positives / len(retrieved)

    @staticmethod
    def recall(retrieved: Set, relevant: Set) -> float:
        """
        Calculate recall: fraction of relevant documents that are retrieved.

        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs

        Returns:
            Recall score between 0 and 1
        """
        if not relevant:
            return 0.0

        true_positives = len(retrieved & relevant)
        return true_positives / len(relevant)

    @staticmethod
    def f1_score(retrieved: Set, relevant: Set) -> float:
        """
        Calculate F1 score: harmonic mean of precision and recall.

        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs

        Returns:
            F1 score between 0 and 1
        """
        prec = SearchMetrics.precision(retrieved, relevant)
        rec = SearchMetrics.recall(retrieved, relevant)

        if prec + rec == 0:
            return 0.0

        return 2 * (prec * rec) / (prec + rec)

    @staticmethod
    def average_precision(
        retrieved_ranked: List[int],
        relevant: Set[int]
    ) -> float:
        """
        Calculate Average Precision (AP).

        Args:
            retrieved_ranked: List of retrieved document IDs in ranked order
            relevant: Set of relevant document IDs

        Returns:
            Average Precision score between 0 and 1
        """
        if not relevant or not retrieved_ranked:
            return 0.0

        precisions = []
        relevant_count = 0

        for i, doc_id in enumerate(retrieved_ranked):
            if doc_id in relevant:
                relevant_count += 1
                precision_at_i = relevant_count / (i + 1)
                precisions.append(precision_at_i)

        if not precisions:
            return 0.0

        return sum(precisions) / len(relevant)

    @staticmethod
    def mean_average_precision(
        queries_results: List[Tuple[List[int], Set[int]]]
    ) -> float:
        """
        Calculate Mean Average Precision (MAP) across multiple queries.

        Args:
            queries_results: List of (retrieved_ranked, relevant) tuples for each query

        Returns:
            MAP score between 0 and 1
        """
        if not queries_results:
            return 0.0

        aps = [
            SearchMetrics.average_precision(retrieved, relevant)
            for retrieved, relevant in queries_results
        ]

        return sum(aps) / len(aps)

    @staticmethod
    def ndcg(
        retrieved_ranked: List[int],
        relevance_scores: Dict[int, float],
        k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG@k).

        Args:
            retrieved_ranked: List of retrieved document IDs in ranked order
            relevance_scores: Dictionary mapping document IDs to relevance scores
            k: Number of top results to consider

        Returns:
            NDCG score between 0 and 1
        """
        if not retrieved_ranked or not relevance_scores:
            return 0.0

        # Calculate DCG
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_ranked[:k]):
            rel = relevance_scores.get(doc_id, 0.0)
            dcg += rel / np.log2(i + 2)  # i+2 because i starts at 0

        # Calculate IDCG (ideal DCG)
        ideal_ranked = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        idcg = 0.0
        for i, (doc_id, rel) in enumerate(ideal_ranked[:k]):
            idcg += rel / np.log2(i + 2)

        if idcg == 0:
            return 0.0

        return dcg / idcg

    @staticmethod
    def mrr(queries_results: List[Tuple[List[int], Set[int]]]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).

        Args:
            queries_results: List of (retrieved_ranked, relevant) tuples

        Returns:
            MRR score
        """
        if not queries_results:
            return 0.0

        reciprocal_ranks = []
        for retrieved, relevant in queries_results:
            for i, doc_id in enumerate(retrieved):
                if doc_id in relevant:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0.0)

        return sum(reciprocal_ranks) / len(reciprocal_ranks)

    @staticmethod
    def evaluate_all(
        retrieved: Set,
        relevant: Set
    ) -> Dict[str, float]:
        """
        Calculate all basic metrics at once.

        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs

        Returns:
            Dictionary with precision, recall, and F1 scores
        """
        prec = SearchMetrics.precision(retrieved, relevant)
        rec = SearchMetrics.recall(retrieved, relevant)
        f1 = SearchMetrics.f1_score(retrieved, relevant)

        return {
            "precision": prec,
            "recall": rec,
            "f1_score": f1
        }
