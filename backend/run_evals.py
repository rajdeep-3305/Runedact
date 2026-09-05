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
    print(f"Analysis: {report['analysis_mention_pct']}%")
    print(f"Concepts: {report['concept_coverage_pct']}%")
    print(f"Invariants: {report['invariant_coverage_pct']}%")
    print(f"Avg latency: {report['avg_latency_ms']} ms")

    categories: dict = {}
    for r in report["results"]:
        categories.setdefault(r.get("category", "general"), []).append(r)

    print("\nBy category:")
    for cat, samples in categories.items():
        avg_concepts = round(sum(s["concepts_pct"] for s in samples) / len(samples), 1)
        avg_invs = round(sum(s["invs_pct"] for s in samples) / len(samples), 1)
        print(f"  {cat:<36} n={len(samples)}  concepts={avg_concepts}%  invs={avg_invs}%")


if __name__ == "__main__":
    main()
