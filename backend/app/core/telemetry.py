import threading
from collections import defaultdict
from typing import Dict


class TelemetryStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._request_count = 0
        self._status_buckets: Dict[str, int] = defaultdict(int)
        self._path_latency_ms: Dict[str, float] = defaultdict(float)
        self._path_hits: Dict[str, int] = defaultdict(int)
        self._sandbox_status_counts: Dict[str, int] = defaultdict(int)

    def record_request(self, path: str, status_code: int, latency_ms: float) -> None:
        key = f"{status_code // 100}xx"
        with self._lock:
            self._request_count += 1
            self._status_buckets[key] += 1
            self._path_latency_ms[path] += latency_ms
            self._path_hits[path] += 1

    def record_sandbox_status(self, status: str) -> None:
        with self._lock:
            self._sandbox_status_counts[status] += 1

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            avg_latency = {
                path: round(self._path_latency_ms[path] / hits, 2)
                for path, hits in self._path_hits.items()
                if hits > 0
            }
            return {
                "request_count": self._request_count,
                "status_buckets": dict(self._status_buckets),
                "path_avg_latency_ms": avg_latency,
                "sandbox_status_counts": dict(self._sandbox_status_counts),
            }


telemetry = TelemetryStore()
