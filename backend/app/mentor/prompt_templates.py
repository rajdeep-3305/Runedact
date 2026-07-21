MENTOR_SYSTEM_PROMPT = """You are a coding mentor helping a learner debug their code without giving away the answer.

Rules:
1. Never provide the complete solution or a full working implementation.
2. Never output multi-line code or copy-paste blocks.
3. Match the requested hint level:
   - Level 1 (Conceptual): ask a probing question about the approach or data structures.
   - Level 2 (Algorithmic): point toward the invariant, edge cases, or data structure choice.
   - Level 3 (Targeted Fix): pinpoint the logic flaw or failing test case and where to look.
4. Use the provided AST metrics and sandbox failures to make the advice specific.
5. Keep it under 150 words and end with a question the learner can act on.
"""


def build_mentor_prompt(
    problem_title: str,
    problem_desc: str,
    student_code: str,
    ast_summary: dict,
    sandbox_result: dict,
    hint_level: int,
    user_query: str = "",
) -> str:
    level_names = {1: "Level 1 (Conceptual)", 2: "Level 2 (Algorithmic)", 3: "Level 3 (Targeted Fix)"}

    failures = [
        f"got {tc.get('got')}, expected {tc.get('expected')}"
        for tc in sandbox_result.get("test_results", [])
        if not tc.get("passed", False)
    ]
    failure_summary = "; ".join(failures[:2]) or sandbox_result.get("stderr") or "none"

    return f"""Problem: {problem_title}
Problem Summary: {problem_desc}

Learner's Current Code:
```python
{student_code}
```

AST Metrics:
{ast_summary.get('structured_prompt_block', '{}')}

Sandbox Execution Results:
- Status: {sandbox_result.get('status', 'not_run')}
- Execution Time: {sandbox_result.get('execution_time_ms', 0)} ms
- Failing Details: {failure_summary}

Requested Hint Level: {level_names.get(hint_level, 'Level 1')}
Learner's Question / Confusion: {user_query or "I am stuck or my tests are failing. Can you guide me?"}
"""
