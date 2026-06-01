"""
Evaluation Metrics
──────────────────
Tracks and computes performance metrics across multiple pipeline runs.
"""

from typing import List, Dict


def calculate_success_rate(results: List[Dict]) -> float:
    """Percentage of runs where critic returned PASS."""
    if not results:
        return 0.0
    passed = sum(1 for r in results if r.get("decision") == "PASS")
    return round(passed / len(results), 4)


def calculate_avg_confidence(results: List[Dict]) -> float:
    """Average confidence score across all runs."""
    if not results:
        return 0.0
    scores = [r.get("confidence_score", 0.0) for r in results]
    return round(sum(scores) / len(scores), 4)


def calculate_avg_retries(results: List[Dict]) -> float:
    """Average number of retries per run."""
    if not results:
        return 0.0
    retries = [r.get("retry_count", 0) for r in results]
    return round(sum(retries) / len(retries), 4)


def calculate_avg_retrieval_score(results: List[Dict]) -> float:
    """Average retrieval quality score."""
    if not results:
        return 0.0
    scores = [r.get("retrieval_score", 0.0) for r in results]
    return round(sum(scores) / len(scores), 4)


def summarise(results: List[Dict]) -> Dict:
    """Return a full evaluation summary dict."""
    return {
        "total_runs":          len(results),
        "success_rate":        calculate_success_rate(results),
        "avg_confidence":      calculate_avg_confidence(results),
        "avg_retries":         calculate_avg_retries(results),
        "avg_retrieval_score": calculate_avg_retrieval_score(results)
    }