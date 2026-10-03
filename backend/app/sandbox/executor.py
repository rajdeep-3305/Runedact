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
from app.core.telemetry import telemetry


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
        from app.sandbox.problems import PROBLEMS

        problem = PROBLEMS.get(problem_id)
        if problem is None:
            return self._error("error", f"Problem '{problem_id}' not found.")
        return self.run_with_harness(code, problem["harness_code"])

    def run_with_harness(self, code: str, harness_code: str) -> Dict[str, Any]:
        full_code = f"{code}\n\n{harness_code}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(full_code)
            tmp_path = tmp.name

        start = time.perf_counter()
        try:
            if settings.SANDBOX_MODE.lower() == "docker":
                result = self._run_in_docker(tmp_path, start)
            else:
                result = self._run_in_process(tmp_path, start)
            telemetry.record_sandbox_status(result["status"])
            return result

        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            result = self._error(
                "time_limit_exceeded",
                f"Wall-clock limit exceeded ({self.cpu_timeout_sec}s). Process terminated.",
                -signal.SIGKILL,
                duration_ms,
            )
            telemetry.record_sandbox_status(result["status"])
            return result
        except Exception as e:
            result = self._error("error", str(e), -1)
            telemetry.record_sandbox_status(result["status"])
            return result
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _run_in_process(self, tmp_path: str, start: float) -> Dict[str, Any]:
        proc = subprocess.Popen(
            [sys.executable, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=self._apply_limits,
        )
        stdout, stderr = proc.communicate(timeout=self.cpu_timeout_sec + 0.5)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return self._parse_execution_result(stdout, stderr, proc.returncode, duration_ms)

    def _run_in_docker(self, tmp_path: str, start: float) -> Dict[str, Any]:
        cmd = [
            "docker",
            "run",
            "--rm",
            "--read-only",
            "--pids-limit",
            str(self.max_processes),
            "--memory",
            f"{self.memory_limit_mb}m",
            "--cpus",
            "1",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=16m",
            "-v",
            f"{tmp_path}:/workspace/main.py:ro",
            "-w",
            "/workspace",
        ]
        if settings.SANDBOX_DISABLE_NETWORK:
            cmd.extend(["--network", "none"])
        cmd.extend([settings.SANDBOX_DOCKER_IMAGE, "python", "main.py"])

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(timeout=self.cpu_timeout_sec + 1.0)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        if proc.returncode != 0 and "docker: not found" in stderr.lower():
            return self._error("error", "docker mode enabled but docker is unavailable", proc.returncode, duration_ms)
        return self._parse_execution_result(stdout, stderr, proc.returncode, duration_ms)

    def _parse_execution_result(
        self, stdout: str, stderr: str, return_code: int, duration_ms: float
    ) -> Dict[str, Any]:
        if return_code != 0:
            if return_code in (-signal.SIGXCPU, -signal.SIGKILL):
                return self._error(
                    "time_limit_exceeded",
                    f"CPU time limit exceeded ({self.cpu_timeout_sec}s).",
                    return_code,
                    duration_ms,
                )
            if "MemoryError" in stderr or return_code == -signal.SIGSEGV:
                return self._error(
                    "memory_limit_exceeded",
                    f"Memory limit exceeded ({self.memory_limit_mb}MB).",
                    return_code,
                    duration_ms,
                )
            if "SyntaxError" in stderr or "IndentationError" in stderr:
                return self._error("compilation_error", stderr, return_code, duration_ms)
            return self._error("runtime_error", stderr, return_code, duration_ms)

        try:
            lines = stdout.strip().split("\n")
            test_results: List[Dict[str, Any]] = json.loads(lines[-1] if lines else "")
        except json.JSONDecodeError:
            return self._error("runtime_error", stderr, return_code, duration_ms)

        for tc in test_results:
            if tc.get("hidden"):
                tc.pop("got", None)
                tc.pop("expected", None)

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


sandbox_executor = CodeSandbox()
