"""
Benchmark Runner
────────────────
Runs the graph against a set of test questions and reports metrics.

Usage:
    python -m evaluation.benchmark
"""

from app.graph import graph
from evaluation.metrics import summarise


BENCHMARK_QUESTIONS = [
    "Explain the architecture of the system.",
    "What retrieval strategy is used?",
    "How does the critic node work?",
    "What happens when the confidence score is low?",
    "Describe the retry mechanism."
]


def run_benchmark():
    results = []

    for i, question in enumerate(BENCHMARK_QUESTIONS, 1):
        print(f"\n[{i}/{len(BENCHMARK_QUESTIONS)}] Running: {question}")

        state = {
            "question":            question,
            "rewritten_question":  "",
            "previous_questions":  [],
            "documents":           [],
            "answer":              "",
            "decision":            "",
            "retry_count":         0,
            "retrieval_score":     0.0,
            "confidence_score":    0.0
        }

        result = graph.invoke(state)
        results.append(result)

        print(f"  Decision    : {result.get('decision')}")
        print(f"  Confidence  : {result.get('confidence_score')}")
        print(f"  Retries     : {result.get('retry_count')}")

    print("\n" + "="*50)
    print("  BENCHMARK SUMMARY")
    print("="*50)
    summary = summarise(results)
    for k, v in summary.items():
        print(f"  {k:<25}: {v}")
    print("="*50 + "\n")

    return summary


if __name__ == "__main__":
    run_benchmark()