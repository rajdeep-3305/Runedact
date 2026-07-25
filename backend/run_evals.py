#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import Base, engine
from app.evals.harness import eval_harness


def main():
    Base.metadata.create_all(bind=engine)
    print("Running evaluation benchmark over the dataset...")

    report = eval_harness.run_benchmark(save_to_db=True)

    print(f"Samples: {report['total_samples']}")
    print(f"Leak rate: {report['leak_rate_percentage']}%")
    print(f"Quality: {report['quality_score']}/100")
    print(f"Faithfulness: {report['faithfulness_score']}/100")
    print(f"Answer relevance: {report['answer_relevance_score']}/100")
    print(f"Context recall: {report['context_recall_score']}/100")
    print(f"Avg latency: {report['avg_latency_ms']} ms")

    categories: dict = {}
    for r in report["results"]:
        categories.setdefault(r.get("category", "general"), []).append(r)

    print("\nBy category:")
    for cat, samples in categories.items():
        avg_rel = round(sum(s["answer_relevance"] for s in samples) / len(samples), 1)
        avg_rec = round(sum(s["context_recall"] for s in samples) / len(samples), 1)
        print(f"  {cat:<36} n={len(samples)}  relevance={avg_rel}%  recall={avg_rec}%")


if __name__ == "__main__":
    main()
