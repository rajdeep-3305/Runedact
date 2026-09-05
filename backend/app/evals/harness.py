import json
import os
import time
from typing import Any, Dict, List

from app.core.database import SessionLocal
from app.evals.metrics import (
    covers_concepts,
    covers_invariants,
    hint_quality_score,
    mentions_analysis,
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
        totals = {"analysis": 0.0, "concepts": 0.0, "invariants": 0.0, "quality": 0.0}
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

            analysis = mentions_analysis(content, ast_summary, item["problem_id"])
            concepts_hit = covers_concepts(content, item.get("expected_flaw", ""), concepts)
            invs_hit = covers_invariants(content, concepts, invariants)
            quality = hint_quality_score(content)

            if leaked:
                leaks += 1

            totals["analysis"] += analysis
            totals["concepts"] += concepts_hit
            totals["invariants"] += invs_hit
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
                    "analysis_pct": analysis,
                    "concepts_pct": concepts_hit,
                    "invs_pct": invs_hit,
                    "quality_score": quality,
                    "latency_ms": latency,
                }
            )

        n = max(1, len(results))
        report = {
            "benchmark_name": "hint quality",
            "total_samples": len(results),
            "leak_rate_percentage": round(leaks / n * 100.0, 1),
            "analysis_mention_pct": round(totals["analysis"] / n, 1),
            "concept_coverage_pct": round(totals["concepts"] / n, 1),
            "invariant_coverage_pct": round(totals["invariants"] / n, 1),
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
