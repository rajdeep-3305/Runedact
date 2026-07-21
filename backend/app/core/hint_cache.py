import time
from typing import Any, Dict, List, Optional


class HintCache:
    """Exact-match cache for generated hints.

    Keyed on problem, hint level, and the analyzer's verdict so identical
    situations don't pay the LLM cost twice.
    """

    def __init__(self, max_entries: int = 512):
        self.max_entries = max_entries
        self._entries: Dict[tuple, Dict[str, Any]] = {}

    @staticmethod
    def _key(
        ast_data: Dict[str, Any],
        problem_id: str,
        hint_level: int,
        sandbox_status: Optional[str],
    ) -> tuple:
        return (
            problem_id,
            hint_level,
            sandbox_status,
            ast_data.get("estimated_complexity"),
            tuple(ast_data.get("anti_patterns", [])),
        )

    def query(
        self,
        ast_data: Dict[str, Any],
        problem_id: str,
        hint_level: int,
        sandbox_status: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        key = self._key(ast_data, problem_id, hint_level, sandbox_status)
        hit = self._entries.get(key)
        if hit is None:
            return None

        return {
            "content": hit["content"],
            "provider": "hint-cache",
            "latency_ms": round((time.perf_counter() - hit["created_at"]) * 1000, 2),
        }

    def index(
        self,
        ast_data: Dict[str, Any],
        problem_id: str,
        hint_level: int,
        content: str,
        sandbox_status: Optional[str] = None,
    ) -> None:
        key = self._key(ast_data, problem_id, hint_level, sandbox_status)
        if key in self._entries:
            return

        if len(self._entries) >= self.max_entries:
            self._entries.pop(next(iter(self._entries)))

        self._entries[key] = {"content": content, "created_at": time.perf_counter()}


hint_cache = HintCache()
