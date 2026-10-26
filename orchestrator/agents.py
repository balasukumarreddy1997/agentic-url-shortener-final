"""Deterministic, executable engineering agents for a reproducible local demo.

These adapters inspect the checked-out repository, run its focused test suite, and
write reviewable artifacts. They intentionally do not make arbitrary source edits.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class AgentError(RuntimeError):
<<<<<<< HEAD
    """A task attempt failed. Retryable by default (transient failures, flaky tools)."""

    retryable = True


class GateBlocked(AgentError):
    """A gate evaluated real evidence and said no. Retrying cannot change the answer."""

    retryable = False
=======
    pass
>>>>>>> origin/main


class AgentRegistry:
    def __init__(self, project_root: str | Path | None = None, test_timeout_seconds: int = 60):
        self.project_root = Path(project_root or os.getenv("PROJECT_ROOT", Path.cwd())).resolve()
        self.test_timeout_seconds = test_timeout_seconds
<<<<<<< HEAD
        artifacts = os.getenv("AGENTIC_ARTIFACTS_DIR")
        self.artifacts_root = (
            Path(artifacts).resolve() if artifacts else self.project_root / ".agentic-artifacts"
        )

    def _artifact(self, ctx: dict[str, Any], name: str, content: dict[str, Any]) -> str:
        run_id = str(ctx.get("run_id", "manual-run"))
        target = self.artifacts_root / run_id
        target.mkdir(parents=True, exist_ok=True)
        path = target / name
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            return str(path.relative_to(self.project_root))
        except ValueError:
            return str(path)
=======

    def _artifact(self, ctx: dict[str, Any], name: str, content: dict[str, Any]) -> str:
        run_id = str(ctx.get("run_id", "manual-run"))
        target = self.project_root / ".agentic-artifacts" / run_id
        target.mkdir(parents=True, exist_ok=True)
        path = target / name
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return str(path.relative_to(self.project_root))
>>>>>>> origin/main

    def execute(self, task_id: str, run_context: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "understand": self._understand,
<<<<<<< HEAD
            "clarify": self._clarify,
=======
>>>>>>> origin/main
            "design": self._design,
            "implement_api": self._inspect_api,
            "implement_orchestrator": self._inspect_orchestrator,
            "tests": self._tests,
            "security_review": self._security,
            "docs": self._docs,
            "release_gate": self._release,
        }
        if task_id not in handlers:
            raise AgentError(f"No agent registered for task: {task_id}")
        return handlers[task_id](run_context)

    def _require_file(self, relative: str) -> Path:
        path = self.project_root / relative
        if not path.is_file():
            raise AgentError(f"Required project file is missing: {relative}")
        return path

    def _understand(self, ctx):
        req = ctx.get("requirement", "")
        scenario = ctx.get("scenario", "greenfield")
        assumptions = ["HTTP and HTTPS destinations only", "SQLite is used for the local prototype"]
        ambiguities = []
        for keyword, question in [
            ("expir", "What is the URL expiration policy?"),
            ("auth", "What authentication and ownership model is required?"),
            ("rate limit", "What rate limits and abuse thresholds are required?"),
        ]:
            if keyword not in req.lower():
                ambiguities.append(question)
        if scenario == "ambiguous":
            ctx["human_questions"] = ambiguities or [
                "Confirm acceptance criteria and operational constraints."
            ]
        result = {
            "scenario": scenario,
            "normalized_requirement": req.strip(),
            "acceptance_criteria": [
                "create short URL",
                "redirect and record click",
                "return analytics",
                "validate requests",
                "run executable tests",
            ],
            "assumptions": assumptions,
            "open_questions": ambiguities,
            "human_questions": ctx.get("human_questions", []),
        }
        result["artifact_path"] = self._artifact(ctx, "requirements.json", result)
        return result

<<<<<<< HEAD
    def _clarify(self, ctx):
        """Turn human answers into explicit, traceable requirement decisions."""
        questions = ctx.get("human_questions", [])
        answers = ctx.get("clarifications", {})
        unanswered = [q for q in questions if not str(answers.get(q, "")).strip()]
        if unanswered:
            # The engine only runs this task after input is supplied, so reaching here means
            # the answers were incomplete. Asking again will not help; a human must respond.
            raise GateBlocked(f"Unanswered clarification questions: {unanswered}")
        result = {
            "resolved": [{"question": q, "answer": answers[q]} for q in questions],
            "answered_by": ctx.get("clarified_by"),
        }
        result["artifact_path"] = self._artifact(ctx, "clarifications.json", result)
        return result

=======
>>>>>>> origin/main
    def _design(self, ctx):
        result = {
            "scenario": ctx.get("scenario"),
            "components": [
                "FastAPI",
                "URLService",
                "SQLiteStore",
                "WorkflowEngine",
                "AgentRegistry",
                "WorkflowRepository",
            ],
            "execution_model": "dependency DAG; independent ready tasks execute concurrently",
            "governance": [
                "human approval for high-impact tasks",
                "audit events",
                "bounded retries",
                "safe-stop",
            ],
            "open_questions": ctx.get("outputs", {})
            .get("understand", {})
            .get("open_questions", []),
<<<<<<< HEAD
            "resolved_clarifications": ctx.get("outputs", {})
            .get("clarify", {})
            .get("resolved", []),
=======
>>>>>>> origin/main
        }
        result["artifact_path"] = self._artifact(ctx, "architecture.json", result)
        return result

    def _inspect_api(self, ctx):
        required = ["app/main.py", "app/schemas.py", "app/service.py", "app/store.py"]
        files = {name: self._require_file(name) for name in required}
        return {
            "operation": "repository_inspection",
            "status": "passed",
            "files_verified": {name: path.stat().st_size for name, path in files.items()},
            "note": "Verified the existing API modules; this agent does not claim to author arbitrary source changes.",
        }

    def _inspect_orchestrator(self, ctx):
        required = [
            "orchestrator/engine.py",
            "orchestrator/planner.py",
            "orchestrator/agents.py",
            "orchestrator/persistence.py",
        ]
        files = {name: self._require_file(name) for name in required}
        graph = ctx.get("outputs", {}).get("design", {}).get("execution_model", "")
        return {
            "operation": "repository_inspection",
            "status": "passed",
            "files_verified": {name: path.stat().st_size for name, path in files.items()},
            "dependency_model": graph,
            "note": "Verified orchestration modules and persistence adapter.",
        }

    def _tests(self, ctx):
        test_file = self._require_file("tests/test_url_shortener.py")
        cmd = [sys.executable, "-m", "pytest", "-q", str(test_file), "--disable-warnings"]
        try:
            completed = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.test_timeout_seconds,
                check=False,
                env={**os.environ, "AGENTIC_WORKFLOW_TEST_RUN": "1"},
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentError(
                f"Focused pytest validation timed out after {self.test_timeout_seconds}s"
            ) from exc
        evidence = {
            "command": "python -m pytest -q tests/test_url_shortener.py --disable-warnings",
            "exit_code": completed.returncode,
            "passed": completed.returncode == 0,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-4000:],
        }
        evidence["artifact_path"] = self._artifact(ctx, "test-evidence.json", evidence)
        if completed.returncode != 0:
            raise AgentError(f"Focused pytest validation failed; see {evidence['artifact_path']}")
        return evidence

<<<<<<< HEAD
    # Destinations the shortener must refuse. Checked against the real request schema, so
    # the review fails if validation regresses, not just if a string disappears from a file.
    DISALLOWED_PROBES = (
        "http://localhost/",
        "http://127.0.0.1/",
        "http://10.0.0.5/",
        "http://169.254.169.254/latest/meta-data",
        "http://[::ffff:127.0.0.1]/",
        "ftp://example.com/",
    )

    def _security(self, ctx):
        self._require_file("app/schemas.py")
        store = self._require_file("app/store.py").read_text(encoding="utf-8")
        from pydantic import ValidationError

        from app.schemas import ShortenRequest

        accepted = []
        for url in self.DISALLOWED_PROBES:
            try:
                ShortenRequest(url=url)
                accepted.append(url)
            except ValidationError:
                pass
        try:
            ShortenRequest(url="https://example.com", custom_code="docs")
            reserved_enforced = False
        except ValidationError:
            reserved_enforced = True
        checks = {
            "rejects_non_public_destinations": not accepted,
            "reserved_codes_enforced": reserved_enforced,
            "parameterized_sql": "WHERE code = ?" in store and "VALUES (?, ?, ?)" in store,
            "no_sql_string_formatting": 'f"SELECT' not in store and "% (" not in store,
=======
    def _security(self, ctx):
        schema = self._require_file("app/schemas.py").read_text(encoding="utf-8")
        store = self._require_file("app/store.py").read_text(encoding="utf-8")
        checks = {
            "http_url_schema": "AnyHttpUrl" in schema,
            "local_host_rejection": "localhost" in schema and "127.0.0.1" in schema,
            "parameterized_sql": "WHERE code = ?" in store and "VALUES (?, ?, ?)" in store,
>>>>>>> origin/main
            "workflow_persistence": (self.project_root / "orchestrator/persistence.py").is_file(),
        }
        findings = [name for name, passed in checks.items() if not passed]
        result = {
            "status": "passed_with_findings" if findings else "checks_passed",
            "checks": checks,
            "findings": findings,
<<<<<<< HEAD
            "accepted_disallowed_destinations": accepted,
=======
>>>>>>> origin/main
            "residual_risks": [
                "No authentication or per-user ownership",
                "No API rate limiting",
                "Destination reputation and phishing controls are not implemented",
<<<<<<< HEAD
                "DNS names resolving to private addresses are not detected",
=======
>>>>>>> origin/main
            ],
        }
        result["artifact_path"] = self._artifact(ctx, "security-review.json", result)
        return result

    def _docs(self, ctx):
        readme = self._require_file("README.md")
        status = self._require_file("SUBMISSION_STATUS.md")
        result = {
            "status": "verified",
            "artifacts": [
                str(readme.relative_to(self.project_root)),
                str(status.relative_to(self.project_root)),
            ],
            "setup_documented": "pip install -e" in readme.read_text(encoding="utf-8"),
            "test_command_documented": "pytest -q" in readme.read_text(encoding="utf-8"),
        }
        result["artifact_path"] = self._artifact(ctx, "documentation-check.json", result)
        return result

    def _release(self, ctx):
        outputs = ctx.get("outputs", {})
        tests = outputs.get("tests", {})
        security = outputs.get("security_review", {})
        docs = outputs.get("docs", {})
        blockers = []
        if tests.get("passed") is not True:
            blockers.append("No successful executable test evidence")
        if not security.get("checks") or security.get("findings"):
            blockers.append("Security review is incomplete or has failed checks")
        if (
            docs.get("setup_documented") is not True
            or docs.get("test_command_documented") is not True
        ):
            blockers.append("Setup or test instructions are missing")
<<<<<<< HEAD
        result = {
=======
        return {
>>>>>>> origin/main
            "ready": not blockers,
            "blockers": blockers,
            "evidence": {
                "test_exit_code": tests.get("exit_code"),
                "security_checks": security.get("checks"),
                "documentation_verified": docs.get("status") == "verified",
            },
<<<<<<< HEAD
            "note": "Evidence gate plus human approval; both must pass for release.",
        }
        result["artifact_path"] = self._artifact(ctx, "release-gate.json", result)
        if blockers:
            # The gate must fail closed. Returning ready=False while the task "succeeds"
            # would let a run reach `succeeded` with known blockers.
            raise GateBlocked(f"Release blocked: {blockers}")
        return result
=======
            "note": "Advisory gate only; final release decision belongs to a human reviewer.",
        }
>>>>>>> origin/main
