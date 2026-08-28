import json
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import (
    ASTAnalysisRequest,
    ASTAnalysisResponse,
    EvalReportResponse,
    LeetCodeProblemDetail,
    LeetCodeProblemSummary,
    MentorHintRequest,
    MentorHintResponse,
    ProblemDetail,
    ProblemSummary,
    RunCodeRequest,
    RunCodeResponse,
)
from app.ast_analyzer.python_ast import analyze_code_ast
from app.core.database import get_db
from app.evals.harness import eval_harness
from app.leetcode.client import LeetCodeError, leetcode_client
from app.mentor.agent import mentor_agent
from app.models.submission import EvalRun, MentorDialogue, Submission
from app.sandbox.executor import sandbox_executor
from app.sandbox.problems import PROBLEMS

logger = logging.getLogger(__name__)

api_router = APIRouter()


@api_router.get("/problems", response_model=List[ProblemSummary])
def list_problems():
    return [
        ProblemSummary(
            id=p["id"], title=p["title"], difficulty=p["difficulty"], tags=p["tags"]
        )
        for p in PROBLEMS.values()
    ]


@api_router.get("/problems/{problem_id}", response_model=ProblemDetail)
def get_problem_details(problem_id: str):
    problem = PROBLEMS.get(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    return ProblemDetail(
        id=problem["id"],
        title=problem["title"],
        difficulty=problem["difficulty"],
        tags=problem["tags"],
        description=problem["description"],
        constraints=problem["constraints"],
        starter_code=problem["starter_code"],
        visible_test_cases=[
            tc for tc in problem["test_cases"] if not tc.get("hidden", False)
        ],
    )


@api_router.post("/run", response_model=RunCodeResponse)
def execute_code(req: RunCodeRequest, db: Session = Depends(get_db)):
    result = sandbox_executor.run_submission(req.problem_id, req.code)
    test_results = result.get("test_results", [])

    try:
        db.add(
            Submission(
                problem_id=req.problem_id,
                code=req.code,
                status=result["status"],
                execution_time_ms=result["execution_time_ms"],
                test_results=json.dumps(test_results),
            )
        )
        db.commit()
    except Exception:
        logger.exception("Failed to save submission")
        db.rollback()

    return RunCodeResponse(
        status=result["status"],
        exit_code=result.get("exit_code", 0),
        execution_time_ms=result["execution_time_ms"],
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        test_results=test_results,
        passed_count=sum(1 for tc in test_results if tc.get("passed", False)),
        total_count=len(test_results),
    )


@api_router.post("/analyze", response_model=ASTAnalysisResponse)
def analyze_ast(req: ASTAnalysisRequest):
    return analyze_code_ast(req.code)


@api_router.post("/mentor/hint", response_model=MentorHintResponse)
def get_mentor_hint(req: MentorHintRequest, db: Session = Depends(get_db)):
    sandbox_result = sandbox_executor.run_submission(req.problem_id, req.code)

    # a dialogue is always tied to the submission it was asked about
    submission_id = None
    try:
        submission = Submission(
            problem_id=req.problem_id,
            code=req.code,
            status=sandbox_result["status"],
            execution_time_ms=sandbox_result["execution_time_ms"],
            test_results=json.dumps(sandbox_result.get("test_results", [])),
        )
        db.add(submission)
        db.commit()
        submission_id = submission.id
    except Exception:
        logger.exception("Failed to save submission")
        db.rollback()

    guidance = mentor_agent.generate_guidance(
        problem_id=req.problem_id,
        code=req.code,
        hint_level=req.hint_level,
        user_query=req.user_query,
        sandbox_result=sandbox_result,
    )

    try:
        db.add(
            MentorDialogue(
                submission_id=submission_id,
                role="assistant",
                hint_level=req.hint_level,
                content=guidance["content"],
                leaked_solution=guidance["leaked_solution"],
                latency_ms=guidance["latency_ms"],
            )
        )
        db.commit()
    except Exception:
        logger.exception("Failed to save mentor dialogue")
        db.rollback()

    return MentorHintResponse(
        problem_id=guidance["problem_id"],
        hint_level=guidance["hint_level"],
        content=guidance["content"],
        leaked_solution=guidance["leaked_solution"],
        ast_insights=guidance["ast_insights"],
        sandbox_status=guidance["sandbox_status"],
        latency_ms=guidance["latency_ms"],
        provider=guidance["provider"],
    )


@api_router.get("/leetcode")
def list_leetcode_problems(limit: int = 50) -> List[LeetCodeProblemSummary]:
    limit = max(1, min(limit, 100))
    try:
        catalog = leetcode_client.catalog(limit=limit)
    except LeetCodeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return [LeetCodeProblemSummary(**p) for p in catalog]


@api_router.get("/leetcode/{slug}")
def get_leetcode_problem(slug: str) -> LeetCodeProblemDetail:
    if not slug.replace("-", "").isalnum() or len(slug) > 80:
        raise HTTPException(status_code=400, detail="invalid problem slug")
    try:
        detail = leetcode_client.question(slug)
    except LeetCodeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return LeetCodeProblemDetail(**detail)


@api_router.post("/evals/run", response_model=EvalReportResponse)
def trigger_eval_benchmark():
    return eval_harness.run_benchmark(save_to_db=True)


@api_router.get("/evals/history")
def get_eval_history(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    runs = (
        db.query(EvalRun)
        .order_by(EvalRun.created_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": r.id,
            "benchmark_name": r.benchmark_name,
            "total_samples": r.total_samples,
            "leak_rate_percentage": r.leak_rate_percentage,
            "quality_score": r.quality_score,
            "avg_latency_ms": r.avg_latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]
