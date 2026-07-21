import re
from typing import Any, Dict, Optional, Tuple

from app.ast_analyzer.python_ast import analyze_code_ast
from app.core.hint_cache import hint_cache

from app.mentor.llm_provider import get_llm_provider
from app.mentor.prompt_templates import MENTOR_SYSTEM_PROMPT, build_mentor_prompt
from app.sandbox.executor import sandbox_executor
from app.sandbox.problems import PROBLEMS


class LeakGuard:

    FUNCTION_DEF_PATTERN = re.compile(r"def\s+[a-zA-Z0-9_]+\s*\([^)]*\):")
    CLASS_DEF_PATTERN = re.compile(r"class\s+[a-zA-Z0-9_]+(\([^)]*\))?:")
    MULTI_LINE_CODE_BLOCK = re.compile(r"```(?:python)?\s*([\s\S]*?)```")
    DISCLOSURE_PHRASES = (
        "here is the complete solution",
        "here is the full code",
        "here's the full implementation",
        "here is the working solution",
        "copy and paste this",
        "replace your function with",
        "the complete code is",
    )

    # Shown when the raw response trips the leak check.
    FALLBACK_RESPONSE = (
        "I can't give you the direct solution, but here are some things to consider:\n"
        "- What must stay true about your state after each step of the loop?\n"
        "- Is there a data structure that would let you replace the inner search with a constant-time lookup?\n"
        "- Which edge case is your code not handling yet?"
    )

    @classmethod
    def is_solution_leak(cls, text: str) -> bool:
        lower = text.lower()
        if any(phrase in lower for phrase in cls.DISCLOSURE_PHRASES):
            return True

        if cls.FUNCTION_DEF_PATTERN.search(text) and (
            "return " in text or len(text.splitlines()) > 4
        ):
            return True

        if cls.CLASS_DEF_PATTERN.search(text):
            return True

        for block in cls.MULTI_LINE_CODE_BLOCK.findall(text):
            lines = [l.strip() for l in block.splitlines() if l.strip() and not l.strip().startswith("#")]
            if len(lines) >= 3:
                return True
            if any(l.startswith(("def ", "for ", "while ", "return ", "class ")) for l in lines):
                return True

        return False

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, bool]:
        if cls.is_solution_leak(text):
            return cls.FALLBACK_RESPONSE, True
        return text, False


class MentorAgent:
    def __init__(self):
        self.llm = get_llm_provider()
        self.cache = hint_cache

    def generate_guidance(
        self,
        problem_id: str,
        code: str,
        hint_level: int = 1,
        user_query: str = "",
        sandbox_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        problem = PROBLEMS.get(problem_id, {})
        title = problem.get("title", problem_id)
        desc = problem.get("description", "")

        ast_summary = analyze_code_ast(code)

        if sandbox_result is None:
            sandbox_result = sandbox_executor.run_submission(problem_id, code)
        sandbox_status = sandbox_result.get("status")

        cached = self.cache.query(ast_summary, problem_id, hint_level, sandbox_status)
        if cached:
            return {
                "problem_id": problem_id,
                "hint_level": hint_level,
                "content": cached["content"],
                "leaked_solution": False,
                "ast_insights": ast_summary,
                "sandbox_status": sandbox_status,
                "latency_ms": cached["latency_ms"],
                "provider": cached["provider"],
            }

        prompt = build_mentor_prompt(
            problem_title=title,
            problem_desc=desc,
            student_code=code,
            ast_summary=ast_summary,
            sandbox_result=sandbox_result,
            hint_level=hint_level,
            user_query=user_query,
        )
        llm_response = self.llm.generate(MENTOR_SYSTEM_PROMPT, prompt)
        content, was_leaked = LeakGuard.sanitize(llm_response.get("content", ""))

        self.cache.index(ast_summary, problem_id, hint_level, content, sandbox_status)

        return {
            "problem_id": problem_id,
            "hint_level": hint_level,
            "content": content,
            "leaked_solution": was_leaked,
            "ast_insights": ast_summary,
            "sandbox_status": sandbox_status,                "latency_ms": llm_response.get("latency_ms", 0.0),
                "provider": llm_response.get("provider", "mock"),
        }


mentor_agent = MentorAgent()
