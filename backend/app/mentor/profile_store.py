from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List


@dataclass
class LearnerProfile:
    recent_statuses: Deque[str] = field(default_factory=lambda: deque(maxlen=10))
    anti_pattern_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    weak_tags: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class ProfileStore:
    def __init__(self) -> None:
        self._profiles: Dict[str, LearnerProfile] = {}

    def _profile(self, session_id: str) -> LearnerProfile:
        if session_id not in self._profiles:
            self._profiles[session_id] = LearnerProfile()
        return self._profiles[session_id]

    def record_attempt(self, session_id: str, status: str, anti_patterns: List[str], tags: List[str]) -> None:
        if not session_id:
            return
        profile = self._profile(session_id)
        profile.recent_statuses.append(status)

        if status != "accepted":
            for tag in tags:
                profile.weak_tags[tag] += 1

        for pattern in anti_patterns:
            profile.anti_pattern_counts[pattern] += 1

    def summarize(self, session_id: str) -> Dict[str, object]:
        if not session_id or session_id not in self._profiles:
            return {"known": False}

        profile = self._profiles[session_id]
        top_patterns = sorted(profile.anti_pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        weak_tags = sorted(profile.weak_tags.items(), key=lambda x: x[1], reverse=True)[:3]
        return {
            "known": True,
            "recent_statuses": list(profile.recent_statuses),
            "top_anti_patterns": [name for name, _ in top_patterns],
            "weak_tags": [name for name, _ in weak_tags],
        }


profile_store = ProfileStore()
