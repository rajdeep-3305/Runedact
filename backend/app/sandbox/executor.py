import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import resource
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.sandbox.problems import PROBLEMS


class CodeSandbox:

    def __init__(
        self,
        cpu_timeout_sec: int = settings.SANDBOX_TIMEOUT_SECONDS,
        memory_limit_mb: int = settings.SANDBOX_MEMORY_LIMIT_MB,
        max_processes: int = settings.SANDBOX_MAX_PROCESSES,
    ):
        self.cpu_timeout_sec = cpu_timeout_sec
        self.memory_limit_mb = memory_limit_mb
        self.max_processes = max_processes

    def _apply_limits(self):
        os.environ["MALLOC_ARENA_MAX"] = "1"
        resource.setrlimit(
            resource.RLIMIT_CPU, (self.cpu_timeout_sec, self.cpu_timeout_sec)
        )
        mem_bytes = self.memory_limit_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (self.max_processes, self.max_processes))
        except (ValueError, OSError):
            pass

    def _error(
        self, status: str, stderr: str, exit_code: int = 0, duration_ms: float = 0.0
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "exit_code": exit_code,
            "stdout": "",
            "stderr": stderr,
            "execution_time_ms": duration_ms,
            "test_results": [],
        }

    def run_submission(self, problem_id: str, code: str) -> Dict[str, Any]:
        if problem_id not in PROBLEMS:
            return self._error("error", f"Problem '{problem_id}' not found.")

        problem = PROBLEMS[problem_id]
        full_code = f"{code}\n\n{problem['harness_code']}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(full_code)
            tmp_path = tmp.name

        start = time.perf_counter()
        try:
            proc = subprocess.Popen(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._apply_limits,
            )
            stdout, stderr = proc.communicate(timeout=self.cpu_timeout_sec + 0.5)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            if proc.returncode != 0:
                if proc.returncode in (-signal.SIGXCPU, -signal.SIGKILL):
                    return self._error(
                        "time_limit_exceeded",
                        f"CPU time limit exceeded ({self.cpu_timeout_sec}s).",
                        proc.returncode,
                        duration_ms,
                    )
                if "MemoryError" in stderr or proc.returncode == -signal.SIGSEGV:
                    return self._error(
                        "memory_limit_exceeded",
                        f"Memory limit exceeded ({self.memory_limit_mb}MB).",
                        proc.returncode,
                        duration_ms,
                    )
                if "SyntaxError" in stderr or "IndentationError" in stderr:
                    return self._error("compilation_error", stderr, proc.returncode, duration_ms)
                return self._error("runtime_error", stderr, proc.returncode, duration_ms)

            try:
                lines = stdout.strip().split("\n")
                test_results: List[Dict[str, Any]] = json.loads(lines[-1] if lines else "")
            except json.JSONDecodeError:
                return self._error("runtime_error", stderr, proc.returncode, duration_ms)

            if any("MemoryError" in str(tc.get("error", "")) for tc in test_results):
                return self._error(
                    "memory_limit_exceeded",
                    f"Memory limit exceeded ({self.memory_limit_mb}MB).",
                    duration_ms=duration_ms,
                )

            all_passed = all(tc.get("passed", False) for tc in test_results)
            return {
                "status": "accepted" if all_passed else "wrong_answer",
                "exit_code": 0,
                "stdout": "\n".join(lines[:-1]),
                "stderr": stderr,
                "execution_time_ms": duration_ms,
                "test_results": test_results,
            }

        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return self._error(
                "time_limit_exceeded",
                f"Wall-clock limit exceeded ({self.cpu_timeout_sec}s). Process terminated.",
                -signal.SIGKILL,
                duration_ms,
            )
        except Exception as e:
            return self._error("error", str(e), -1)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


sandbox_executor = CodeSandbox()
