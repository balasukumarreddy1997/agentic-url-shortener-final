<<<<<<< HEAD
import asyncio
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from orchestrator.agents import AgentError, AgentRegistry
from orchestrator.engine import ExecutionInterrupted, PolicyViolation, WorkflowEngine
=======
from pathlib import Path

import pytest

from orchestrator.engine import WorkflowEngine
>>>>>>> origin/main
from orchestrator.models import Status
from orchestrator.persistence import WorkflowRepository


def make_engine(tmp_path=None):
    if tmp_path is None:
        import tempfile

        tmp_path = Path(tempfile.mkdtemp())
    return WorkflowEngine(repository=WorkflowRepository(str(Path(tmp_path) / "workflows.db")))


<<<<<<< HEAD
=======
@pytest.mark.asyncio
>>>>>>> origin/main
async def test_approval_gate_and_resume(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener with analytics")
    run = await engine.execute(run.id)
    assert run.status == "waiting_approval"
    task = run.tasks["implement_orchestrator"]
    assert task.status == Status.WAITING_APPROVAL
    engine.approve(run.id, task.id, True, "reviewer", "Reviewed scope")
    run = await engine.execute(run.id)
    assert run.status == "waiting_approval"
    # Release gate is another explicit approval checkpoint.
    assert run.tasks["release_gate"].status == Status.WAITING_APPROVAL, {
        k: v.status for k, v in run.tasks.items()
    }
    engine.approve(run.id, "release_gate", True, "release-manager", "Evidence reviewed")
    run = await engine.execute(run.id)
    assert run.status == "succeeded"


<<<<<<< HEAD
=======
@pytest.mark.asyncio
>>>>>>> origin/main
async def test_approval_denial_safe_stops(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id)
    engine.approve(run.id, "implement_orchestrator", False, "reviewer", "Risk too high")
    assert run.status == "blocked"


def test_replan_preserves_lineage_and_resets_work(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("ambiguous", "Build a short URL API")
    run.decisions.append({"approver": "reviewer", "approved": True})
    engine.replan(run.id, "Build short URLs with configurable expiration")
    assert run.replan_count == 1
    assert run.requirement.endswith("configurable expiration")
    assert run.decisions[0]["approver"] == "reviewer"


<<<<<<< HEAD
async def test_rollback_records_actor_and_reason(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    await engine.execute(run.id)  # runs up to the first approval gate
    engine.rollback(run.id, "release regression", "on-call")
    assert run.status == "rolled_back"
    assert run.rollback_count == 1
    rollback = next(e for e in run.audit if e.event == "rollback")
    assert rollback.details["actor"] == "on-call"
    assert "implement_api" in rollback.details["reverted_tasks"]


=======
def test_rollback_records_actor_and_reason(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    engine.rollback(run.id, "release regression", "on-call")
    assert run.status == "rolled_back"
    assert run.rollback_count == 1
    assert run.audit[-1].event == "rollback"


@pytest.mark.asyncio
>>>>>>> origin/main
async def test_replan_requires_fresh_approval_for_new_generation(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id)
    engine.approve(run.id, "implement_orchestrator", True, "reviewer", "Approved first plan")
    run = await engine.execute(run.id)
    assert run.status == "waiting_approval"
    engine.replan(run.id, "Build a URL shortener with expiration")
    run = await engine.execute(run.id)
    assert run.tasks["implement_orchestrator"].status == Status.WAITING_APPROVAL
    # The previous approval is retained as history, but cannot approve a changed plan.
    assert len(run.decisions) == 1
    assert run.decisions[0]["generation"] == 0


<<<<<<< HEAD
=======
@pytest.mark.asyncio
>>>>>>> origin/main
async def test_execute_success_is_idempotent_for_terminal_run(tmp_path):
    engine = make_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id, auto_approve=True)
    assert run.status == "succeeded"
    succeeded_count = engine.metrics["succeeded"]
    audit_count = len(run.audit)
    again = await engine.execute(run.id, auto_approve=True)
    assert again.status == "succeeded"
    assert engine.metrics["succeeded"] == succeeded_count
    assert len(run.audit) == audit_count


def test_all_scenarios_create_dependency_aware_plans(tmp_path):
    engine = make_engine(tmp_path)
    for scenario in ("greenfield", "brownfield", "ambiguous"):
        run = engine.create_run(scenario, "Build a URL shortener")
        engine._validate_graph(run)
        assert "understand" in run.tasks
        assert "release_gate" in run.tasks
    ambiguous = engine.create_run("ambiguous", "Build a URL shortener")
    assert ambiguous.tasks["understand"].output["assumptions_required"] is True


def test_workflow_survives_engine_restart(tmp_path):
    db_path = str(tmp_path / "durable.db")
    first = WorkflowEngine(repository=WorkflowRepository(db_path))
    run = first.create_run("ambiguous", "Build a short URL API")
    run_id = run.id
    run.record("test_marker", marker="persisted")
    first._persist(run)
    restarted = WorkflowEngine(repository=WorkflowRepository(db_path))
    recovered = restarted.get_run(run_id)
    assert recovered.id == run_id
    assert recovered.scenario == "ambiguous"
    assert recovered.audit[-1].event == "test_marker"
    assert recovered.audit[-1].details["marker"] == "persisted"


def test_security_agent_checks_real_repository_files():
    from orchestrator.agents import AgentRegistry

    project_root = Path(__file__).resolve().parents[1]
    agent = AgentRegistry(project_root=project_root)
    result = agent.execute(
        "security_review",
        {
            "run_id": "test-security",
            "scenario": "greenfield",
            "requirement": "Build shortener",
            "outputs": {},
        },
    )
<<<<<<< HEAD
    assert result["checks"]["rejects_non_public_destinations"] is True
    assert result["checks"]["reserved_codes_enforced"] is True
    assert result["checks"]["parameterized_sql"] is True
    assert result["findings"] == []


# ---------------------------------------------------------------------------
# Regression and failure-injection tests added during review.
# FastAgents replaces the pytest subprocess with canned evidence so these stay fast and
# deterministic; the real subprocess path is covered by the tests above.
# ---------------------------------------------------------------------------


class FastAgents(AgentRegistry):
    def __init__(self, **overrides):
        super().__init__(project_root=Path(__file__).resolve().parents[1])
        self.overrides = overrides
        self.calls: dict[str, int] = {}

    def execute(self, task_id, ctx):
        self.calls[task_id] = self.calls.get(task_id, 0) + 1
        if task_id in self.overrides:
            return self.overrides[task_id](self, ctx, self.calls[task_id])
        if task_id == "tests":
            return {"passed": True, "exit_code": 0, "status": "passed"}
        return super().execute(task_id, ctx)


def fast_engine(tmp_path, **overrides):
    return WorkflowEngine(
        agents=FastAgents(**overrides),
        repository=WorkflowRepository(str(tmp_path / "wf.db")),
        retry_backoff_seconds=0,
    )


async def test_release_gate_fails_closed_on_blockers(tmp_path):
    """Regression: blockers were reported but the run still ended 'succeeded'."""

    def failing_security(agent, ctx, _):
        out = AgentRegistry._security(agent, ctx)
        out["findings"] = ["parameterized_sql"]
        return out

    engine = fast_engine(tmp_path, security_review=failing_security)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id, auto_approve=True)
    assert run.status == "blocked"
    assert run.tasks["release_gate"].status == Status.BLOCKED
    assert engine.agents.calls["release_gate"] == 1, "gate refusals must not be retried"
    assert engine.metrics["succeeded"] == 0 and engine.metrics["blocked"] == 1


async def test_success_rate_never_exceeds_one_after_replan(tmp_path):
    """Regression: success_rate reached 2.0 after replan + second success."""
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    await engine.execute(run.id, auto_approve=True)
    engine.replan(run.id, "Build a URL shortener v2")
    await engine.execute(run.id, auto_approve=True)
    snap = engine.metrics_snapshot()
    assert snap["succeeded"] == 2 and snap["terminal_outcomes"] == 2
    assert snap["success_rate"] == 1.0


async def test_in_progress_runs_do_not_dilute_success_rate(tmp_path):
    engine = fast_engine(tmp_path)
    done = engine.create_run("greenfield", "Build a URL shortener")
    await engine.execute(done.id, auto_approve=True)
    waiting = engine.create_run("greenfield", "Build a URL shortener")
    await engine.execute(waiting.id)  # parks at an approval gate
    assert engine.metrics_snapshot()["success_rate"] == 1.0


async def test_ambiguous_run_pauses_for_clarification(tmp_path):
    """Regression: ambiguous runs recorded questions but never waited for answers."""
    engine = fast_engine(tmp_path)
    run = engine.create_run("ambiguous", "make links short", requested_by="alice")
    run = await engine.execute(run.id)
    assert run.status == "waiting_input"
    assert run.tasks["clarify"].status == Status.WAITING_INPUT
    assert run.tasks["design"].status == Status.PENDING, "design must not start early"
    questions = run.context["human_questions"]
    assert questions

    with pytest.raises(ValueError, match="Missing answers"):
        engine.clarify(run.id, {questions[0]: "30 days"}, "alice")

    answers = {q: f"answer {i}" for i, q in enumerate(questions)}
    engine.clarify(run.id, answers, "alice")
    run = await engine.execute(run.id)
    assert run.tasks["design"].status == Status.SUCCEEDED
    resolved = run.tasks["design"].output["resolved_clarifications"]
    assert {r["question"] for r in resolved} == set(questions)
    lineage = [d for d in run.decisions if d["type"] == "clarification"]
    assert len(lineage) == len(questions) and all(d["answered_by"] == "alice" for d in lineage)


async def test_replan_invalidates_previous_clarifications(tmp_path):
    engine = fast_engine(tmp_path)
    run = engine.create_run("ambiguous", "make links short")
    await engine.execute(run.id, auto_approve=True)
    engine.replan(run.id, "make links short and expiring")
    run = await engine.execute(run.id)
    assert run.status == "waiting_input"


async def test_requester_cannot_self_approve(tmp_path):
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener", requested_by="alice")
    await engine.execute(run.id)
    with pytest.raises(ValueError, match="own workflow"):
        engine.approve(run.id, "implement_orchestrator", True, "Alice ")
    assert any(e.event == "policy_violation" for e in run.audit)
    engine.approve(run.id, "implement_orchestrator", True, "bob")


async def test_approval_request_carries_upstream_evidence(tmp_path):
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    await engine.execute(run.id)
    engine.approve(run.id, "implement_orchestrator", True, "reviewer")
    await engine.execute(run.id)
    request = [
        e for e in run.audit if e.event == "approval_requested" and e.task_id == "release_gate"
    ][-1]
    assert request.details["upstream_evidence"]["tests"]["passed"] is True


async def test_parallel_branches_actually_overlap(tmp_path):
    """Regression: synchronous agents inside gather() ran one after another."""

    def slow(_agent, _ctx, _n):
        time.sleep(0.3)
        return {"status": "passed"}

    engine = fast_engine(tmp_path, implement_api=slow, implement_orchestrator=slow, docs=slow)
    run = engine.create_run("greenfield", "Build a URL shortener")
    started = time.perf_counter()
    await engine.execute(run.id, auto_approve=True)
    assert time.perf_counter() - started < 0.75, "three 0.3s branches should overlap"


async def test_event_loop_stays_responsive_during_agent_work(tmp_path):
    def slow(_agent, _ctx, _n):
        time.sleep(0.4)
        return {"passed": True, "exit_code": 0}

    engine = fast_engine(tmp_path, tests=slow)
    run = engine.create_run("greenfield", "Build a URL shortener")
    ticks = 0

    async def ticker():
        nonlocal ticks
        while True:
            ticks += 1
            await asyncio.sleep(0.02)

    t = asyncio.create_task(ticker())
    await engine.execute(run.id, auto_approve=True)
    t.cancel()
    assert ticks >= 10


async def test_transient_failure_retries_and_records_mttr(tmp_path):
    def flaky(agent, ctx, attempt):
        if attempt == 1:
            raise AgentError("transient")
        return {"status": "passed"}

    engine = fast_engine(tmp_path, implement_api=flaky)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id, auto_approve=True)
    assert run.status == "succeeded"
    assert run.tasks["implement_api"].attempts == 2
    snap = engine.metrics_snapshot()
    assert snap["retries"] == 1 and snap["recoveries"] == 1 and snap["mttr_ms"] >= 0
    assert any(e.event == "task_recovered" for e in run.audit)


async def test_retry_exhaustion_fails_run_and_blocks_descendants(tmp_path):
    def broken(*_):
        raise AgentError("always broken")

    engine = fast_engine(tmp_path, implement_api=broken)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id, auto_approve=True)
    assert run.status == "failed"
    assert run.tasks["implement_api"].status == Status.FAILED
    assert run.tasks["implement_api"].attempts == 2  # 1 + max_retries
    assert run.tasks["tests"].status == Status.BLOCKED
    assert run.tasks["release_gate"].status == Status.BLOCKED
    assert run.tasks["docs"].status == Status.SUCCEEDED, "independent branch still completes"


async def test_rollback_guards(tmp_path):
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    with pytest.raises(ValueError, match="Nothing to roll back"):
        engine.rollback(run.id, "why", "on-call")
    await engine.execute(run.id, auto_approve=True)
    engine.rollback(run.id, "regression", "on-call")
    with pytest.raises(ValueError, match="already rolled back"):
        engine.rollback(run.id, "again", "on-call")
    assert engine.metrics["rollbacks"] == 1


async def test_concurrent_execute_calls_are_serialized(tmp_path):
    def slow(_agent, _ctx, _n):
        time.sleep(0.1)
        return {"status": "passed"}

    engine = fast_engine(tmp_path, implement_api=slow)
    run = engine.create_run("greenfield", "Build a URL shortener")
    await asyncio.gather(
        engine.execute(run.id, auto_approve=True), engine.execute(run.id, auto_approve=True)
    )
    assert engine.agents.calls["implement_api"] == 1
    assert engine.metrics["succeeded"] == 1


def test_waiting_input_survives_restart(tmp_path):
    db = str(tmp_path / "durable.db")
    first = WorkflowEngine(agents=FastAgents(), repository=WorkflowRepository(db))
    run = first.create_run("ambiguous", "make links short")
    asyncio.run(first.execute(run.id))
    restarted = WorkflowEngine(agents=FastAgents(), repository=WorkflowRepository(db))
    again = restarted.get_run(run.id)
    assert again.status == "waiting_input"
    assert again.tasks["clarify"].status == Status.WAITING_INPUT


def test_api_rejects_auto_approve_without_demo_flag(monkeypatch):
    from app.main import app

    monkeypatch.delenv("ALLOW_DEMO_AUTO_APPROVE", raising=False)
    client = TestClient(app)
    body = {"scenario": "greenfield", "requirement": "Build it", "requested_by": "alice"}
    assert client.post("/api/workflows", json={**body, "auto_approve": True}).status_code == 403
    assert (
        client.post(
            "/api/workflows", json={"scenario": "greenfield", "requirement": "x" * 10}
        ).status_code
        == 422
    )


def test_api_clarify_and_self_approval_flow(monkeypatch):
    from app.main import app
    from orchestrator import api

    monkeypatch.setattr(api.engine, "agents", FastAgents())
    client = TestClient(app)
    run = client.post(
        "/api/workflows",
        json={"scenario": "ambiguous", "requirement": "make links short", "requested_by": "alice"},
    ).json()
    assert run["status"] == "waiting_input"
    questions = run["context"]["human_questions"]
    run = client.post(
        f"/api/workflows/{run['id']}/clarify",
        json={"answers": {q: "yes" for q in questions}, "answered_by": "alice"},
    ).json()
    assert run["status"] == "waiting_approval"
    url = f"/api/workflows/{run['id']}/approve/implement_orchestrator"
    assert client.post(url, json={"approved": True, "approver": "alice"}).status_code == 409
    assert client.post(url, json={"approved": True, "approver": "bob"}).status_code == 200
    assert "mttr_ms" in client.get("/api/workflows/metrics/summary").json()
    assert os.getenv("ALLOW_DEMO_AUTO_APPROVE") is None


# --- Failure scenarios referenced by the risk table in DOCUMENTATION.md ---------------


async def test_db_failure_mid_run_leaves_run_resumable(tmp_path):
    """Regression: a failed state write left the run 'running' forever in memory."""
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    real_save, calls = engine.repository.save_run, {"n": 0}

    def flaky_save(r):
        calls["n"] += 1
        if calls["n"] == 3:
            raise sqlite3.OperationalError("disk I/O error")
        real_save(r)

    engine.repository.save_run = flaky_save
    with pytest.raises(ExecutionInterrupted):
        await engine.execute(run.id)
    assert run.status == "interrupted"
    assert not any(t.status == Status.RUNNING for t in run.tasks.values())
    assert any(e.event == "execution_interrupted" for e in run.audit)

    engine.repository.save_run = real_save
    run = await engine.execute(run.id)  # resume
    assert run.status == "waiting_approval"


def test_process_crash_mid_task_recovers_on_restart(tmp_path):
    db = str(tmp_path / "crash.db")
    first = WorkflowEngine(agents=FastAgents(), repository=WorkflowRepository(db))
    run = first.create_run("greenfield", "Build a URL shortener")
    run.status = "running"
    run.tasks["understand"].status = Status.RUNNING
    first._persist(run)  # simulate the process dying here

    restarted = WorkflowEngine(agents=FastAgents(), repository=WorkflowRepository(db))
    recovered = restarted.get_run(run.id)
    assert recovered.status == "interrupted"
    assert recovered.tasks["understand"].status == Status.READY
    assert recovered.audit[-1].event == "execution_recovered"
    recovered = asyncio.run(restarted.execute(run.id))
    assert recovered.tasks["understand"].status == Status.SUCCEEDED


async def test_hung_test_suite_times_out_and_fails_run(tmp_path, monkeypatch):
    def hang(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="pytest", timeout=kwargs.get("timeout"))

    monkeypatch.setattr(subprocess, "run", hang)
    engine = WorkflowEngine(
        agents=AgentRegistry(project_root=Path(__file__).resolve().parents[1]),
        repository=WorkflowRepository(str(tmp_path / "wf.db")),
        retry_backoff_seconds=0,
    )
    run = engine.create_run("greenfield", "Build a URL shortener")
    run = await engine.execute(run.id, auto_approve=True)
    assert run.status == "failed"
    assert "timed out" in run.tasks["tests"].error
    assert run.tasks["tests"].attempts == 2
    assert run.tasks["release_gate"].status == Status.BLOCKED


def test_cyclic_plan_is_rejected_before_execution(tmp_path):
    engine = fast_engine(tmp_path)
    run = engine.create_run("greenfield", "Build a URL shortener")
    run.tasks["understand"].depends_on = ["release_gate"]
    with pytest.raises(PolicyViolation, match="cycle"):
        asyncio.run(engine.execute(run.id))
    assert all(t.attempts == 0 for t in run.tasks.values())
=======
    assert result["checks"]["http_url_schema"] is True
    assert result["checks"]["parameterized_sql"] is True
>>>>>>> origin/main
