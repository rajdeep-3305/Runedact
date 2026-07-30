import json
import os
import time
from typing import Any, Dict, List

from app.core.database import SessionLocal
from app.evals.metrics import (
    calculate_answer_relevance,
    calculate_context_recall,
    calculate_faithfulness,
    score_quality,
)
from app.mentor.agent import mentor_agent
from app.models.submission import EvalRun

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")


class EvalHarness:
    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path

    def load_dataset(self) -> List[Dict[str, Any]]:
        with open(self.dataset_path) as f:
            return json.load(f)

    def run_benchmark(self, save_to_db: bool = True) -> Dict[str, Any]:
        results = []
        totals = {"faithfulness": 0.0, "relevance": 0.0, "recall": 0.0, "quality": 0.0}
        total_latency = 0.0
        leaks = 0

        for item in self.load_dataset():
            concepts = item.get("ground_truth_concepts", [])
            invariants = item.get("context_invariants", [])

            guidance = mentor_agent.generate_guidance(
                problem_id=item["problem_id"],
                code=item["code"],
                hint_level=2,
            )

            content = guidance["content"]
            leaked = guidance["leaked_solution"]
            latency = guidance["latency_ms"]
            ast_summary = guidance.get("ast_insights", {})

            faithfulness = calculate_faithfulness(content, ast_summary, item["problem_id"])
            relevance = calculate_answer_relevance(content, item.get("expected_flaw", ""), concepts)
            recall = calculate_context_recall(content, concepts, invariants)
            quality = score_quality(content)

            if leaked:
                leaks += 1

            totals["faithfulness"] += faithfulness
            totals["relevance"] += relevance
            totals["recall"] += recall
            totals["quality"] += quality
            total_latency += latency

            results.append(
                {
                    "id": item["id"],
                    "problem_id": item["problem_id"],
                    "category": item.get("category"),
                    "expected_flaw": item.get("expected_flaw"),
                    "hint_generated": content,
                    "leaked_solution": leaked,
                    "faithfulness": faithfulness,
                    "answer_relevance": relevance,
                    "context_recall": recall,
                    "quality_score": quality,
                    "latency_ms": latency,
                }
            )

        n = max(1, len(results))
        report = {
            "benchmark_name": "hint quality",
            "total_samples": len(results),
            "leak_rate_percentage": round(leaks / n * 100.0, 1),
            "faithfulness_score": round(totals["faithfulness"] / n, 1),
            "answer_relevance_score": round(totals["relevance"] / n, 1),
            "context_recall_score": round(totals["recall"] / n, 1),
            "quality_score": round(totals["quality"] / n, 1),
            "avg_latency_ms": round(total_latency / n, 2),
            "results": results,
        }

        if save_to_db:
            self._persist(report)

        return report

    def _persist(self, report: Dict[str, Any]) -> None:
        db = SessionLocal()
        try:
            db.add(
                EvalRun(
                    benchmark_name=report["benchmark_name"],
                    total_samples=report["total_samples"],
                    quality_score=report["quality_score"],
                    leak_rate_percentage=report["leak_rate_percentage"],
                    avg_latency_ms=report["avg_latency_ms"],
                    report_json=json.dumps(report),
                )
            )
            db.commit()
        except Exception:
            pass
        finally:
            db.close()


eval_harness = EvalHarness()
