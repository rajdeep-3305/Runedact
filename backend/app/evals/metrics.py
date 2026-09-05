import re
from typing import Any, Dict, List

CONCEPT_KEYWORDS = (
    "loop",
    "time",
    "complexity",
    "hash",
    "dict",
    "map",
    "stack",
    "pop",
    "coin",
    "dp",
    "cache",
    "invariant",
    "index",
    "condition",
)


def mentions_analysis(hint: str, ast_data: Dict[str, Any], problem_id: str) -> float:
    sentences = [s.strip() for s in re.split(r"[.!?\n]", hint) if len(s.strip().split()) >= 3]
    if not sentences:
        return 100.0

    ast_text = str(ast_data).lower()
    supported = 0
    for sentence in sentences:
        s_lower = sentence.lower()
        is_supported = (
            any(w in s_lower for w in CONCEPT_KEYWORDS)
            or "?" in sentence
            or any(kw in ast_text for kw in s_lower.split() if len(kw) > 4)
        )
        if is_supported:
            supported += 1

    return round(supported / len(sentences) * 100.0, 1)


def covers_concepts(hint: str, expected_flaw: str, ground_truth_concepts: List[str]) -> float:
    if not ground_truth_concepts:
        return 100.0

    hint_lower = hint.lower()
    matched_weight = 0.0
    total_weight = 0.0

    for idx, concept in enumerate(ground_truth_concepts):
        weight = 1.0 / (idx + 1)
        total_weight += weight
        if any(word in hint_lower for word in concept.lower().split()):
            matched_weight += weight

    score = matched_weight / total_weight if total_weight else 1.0
    if "?" in hint:
        score = min(1.0, score + 0.15)

    return round(score * 100.0, 1)


def covers_invariants(hint: str, ground_truth_concepts: List[str], context_invariants: List[str]) -> float:
    targets = ground_truth_concepts + context_invariants
    if not targets:
        return 100.0

    hint_lower = hint.lower()
    recalled = sum(
        1
        for target in targets
        if any(token in hint_lower for token in target.lower().split() if len(token) >= 3)
    )
    return round(recalled / len(targets) * 100.0, 1)


def hint_quality_score(content: str) -> float:
    score = 0.0

    question_count = content.count("?")
    if question_count:
        score += min(40.0, question_count * 25.0)

    words = len(content.split())
    if 20 <= words <= 160:
        score += 25.0
    elif words < 20:
        score += 10.0
    else:
        score += max(0.0, 25.0 - (words - 160) * 0.2)

    gives_function = bool(re.search(r"def\s+\w+\s*\([^)]*\):[\s\S]{20,}return\s+", content))
    score += 25.0 if not gives_function else -40.0

    if any(w in content.lower() for w in ("notice", "consider", "what happens", "think about", "how would", "try", "why", "invariant")):
        score += 10.0

    return max(0.0, min(100.0, round(score, 1)))
