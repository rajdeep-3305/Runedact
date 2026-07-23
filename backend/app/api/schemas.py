from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: List[str]


class ProblemDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: List[str]
    description: str
    constraints: List[str]
    starter_code: Dict[str, str]
    visible_test_cases: List[Dict[str, Any]]


class RunCodeRequest(BaseModel):
    problem_id: str
    code: str


class TestCaseResult(BaseModel):
    test_idx: int
    passed: bool
    got: Optional[Any] = None
    expected: Optional[Any] = None
    error: Optional[str] = None
    hidden: bool = False


class RunCodeResponse(BaseModel):
    status: str
    exit_code: int
    execution_time_ms: float
    stdout: str
    stderr: str
    test_results: List[TestCaseResult]
    passed_count: int
    total_count: int


class ASTAnalysisRequest(BaseModel):
    code: str


class ASTAnalysisResponse(BaseModel):
    syntax_valid: bool
    syntax_error_msg: str
    max_loop_depth: int
    has_recursion: bool
    data_structures: List[str]
    functions_defined: List[str]
    cyclomatic_complexity: int
    anti_patterns: List[str]
    estimated_complexity: str


class MentorHintRequest(BaseModel):
    problem_id: str
    code: str
    hint_level: int = Field(default=1, ge=1, le=3)
    user_query: Optional[str] = ""


class MentorHintResponse(BaseModel):
    problem_id: str
    hint_level: int
    content: str
    leaked_solution: bool
    ast_insights: Dict[str, Any]
    sandbox_status: Optional[str] = None
    latency_ms: float
    provider: str


class EvalReportResponse(BaseModel):
    benchmark_name: str
    total_samples: int
    leak_rate_percentage: float
    faithfulness_score: Optional[float] = 0.0
    answer_relevance_score: Optional[float] = 0.0
    context_recall_score: Optional[float] = 0.0
    quality_score: float
    avg_latency_ms: float
    results: List[Dict[str, Any]]
