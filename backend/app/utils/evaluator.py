"""Evaluation mechanisms for agent outputs."""
from typing import Dict, Any, List
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ResponseEvaluator:
    """Evaluates quality of agent responses."""

    def evaluate_relevance(self, query: str, response: str, source_docs: List[str]) -> float:
        """Evaluate how relevant the response is to the query."""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words.intersection(response_words))
        relevance = min(overlap / max(len(query_words), 1), 1.0)
        return relevance

    def evaluate_completeness(self, response: str) -> float:
        """Evaluate completeness of the response."""
        if not response:
            return 0.0
        word_count = len(response.split())
        if word_count < 20:
            return 0.3
        elif word_count < 100:
            return 0.6
        elif word_count < 500:
            return 0.85
        else:
            return 1.0

    def evaluate_groundedness(self, response: str, source_docs: List[str]) -> float:
        """Evaluate how well-grounded the response is in source documents."""
        if not source_docs:
            return 0.0

        response_words = set(response.lower().split())
        total_overlap = 0
        for doc in source_docs:
            doc_words = set(doc.lower().split())
            overlap = len(response_words.intersection(doc_words))
            total_overlap += overlap

        avg_overlap = total_overlap / len(source_docs)
        groundedness = min(avg_overlap / max(len(response_words), 1), 1.0)
        return min(groundedness * 3, 1.0)  # Scale up

    def evaluate_response(
        self,
        query: str,
        response: str,
        source_docs: List[str],
    ) -> Dict[str, Any]:
        """Comprehensive evaluation of a response."""
        relevance = self.evaluate_relevance(query, response, source_docs)
        completeness = self.evaluate_completeness(response)
        groundedness = self.evaluate_groundedness(response, source_docs)
        overall_score = (relevance * 0.3 + completeness * 0.3 + groundedness * 0.4)

        evaluation = {
            "relevance_score": round(relevance, 3),
            "completeness_score": round(completeness, 3),
            "groundedness_score": round(groundedness, 3),
            "overall_score": round(overall_score, 3),
            "quality_tier": self._get_quality_tier(overall_score),
        }

        logger.debug("Response evaluation", **evaluation)
        return evaluation

    def _get_quality_tier(self, score: float) -> str:
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "acceptable"
        else:
            return "poor"
