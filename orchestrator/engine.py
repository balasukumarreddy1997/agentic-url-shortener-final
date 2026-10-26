import asyncio
<<<<<<< HEAD
import copy
import logging
import time
import uuid
from datetime import datetime

from orchestrator.agents import AgentRegistry
from orchestrator.models import Status, Task, WorkflowRun, now_iso
from orchestrator.persistence import WorkflowRepository
from orchestrator.planner import build_plan

logger = logging.getLogger(__name__)

TERMINAL_RUN_STATES = {"succeeded", "failed", "blocked", "rolled_back"}
SETTLED_TASK_STATES = {Status.SUCCEEDED, Status.SKIPPED, Status.BLOCKED, Status.ROLLED_BACK}
FAILED_TASK_STATES = {Status.FAILED, Status.BLOCKED, Status.ROLLED_BACK}
DEMO_APPROVER = "demo-auto-approval"

=======
import time
import uuid

from orchestrator.agents import AgentRegistry
from orchestrator.models import Status, WorkflowRun, now_iso
from orchestrator.persistence import WorkflowRepository
from orchestrator.planner import build_plan

>>>>>>> origin/main

class WorkflowNotFound(KeyError):
    pass


class ApprovalRequired(RuntimeError):
    pass


class PolicyViolation(RuntimeError):
    pass


<<<<<<< HEAD
class ExecutionInterrupted(RuntimeError):
    """Execution stopped on an infrastructure error. State is preserved and resumable."""


def _iso_to_epoch(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


class WorkflowEngine:
    def __init__(self, agents=None, repository=None, retry_backoff_seconds: float = 0.1):
        self.agents = agents or AgentRegistry()
        self.repository = repository or WorkflowRepository()
        self.retry_backoff_seconds = retry_backoff_seconds
        self.runs: dict[str, WorkflowRun] = self.repository.load_runs()
        self.metrics = self._default_metrics()
        self.metrics.update(self.repository.load_metrics() or {"runs": len(self.runs)})
        # One execution at a time per run. Without this, two concurrent approval requests
        # could each start an execution loop over the same mutable run.
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def _default_metrics():
        return {
            "runs": 0,
            # Terminal outcomes, counted once per plan generation.
            "succeeded": 0,
            "failed": 0,
            "blocked": 0,
            "rolled_back_runs": 0,
            "retries": 0,
            "rollbacks": 0,
            # Agent execution time only, excluding time spent waiting for humans.
            "total_execution_ms": 0.0,
            # Wall clock from plan start to terminal outcome, including human waits.
            "total_lead_time_ms": 0.0,
            # Task-level recovery: first failed attempt -> later successful attempt.
            "recoveries": 0,
            "total_recovery_ms": 0.0,
        }

    def _lock(self, run_id: str) -> asyncio.Lock:
        return self._locks.setdefault(run_id, asyncio.Lock())

=======
class WorkflowEngine:
    def __init__(self, agents=None, repository=None):
        self.agents = agents or AgentRegistry()
        self.repository = repository or WorkflowRepository()
        self.runs: dict[str, WorkflowRun] = self.repository.load_runs()
        self.metrics = self.repository.load_metrics() or {
            "runs": len(self.runs),
            "succeeded": 0,
            "failed": 0,
            "retries": 0,
            "rollbacks": 0,
            "total_latency_ms": 0.0,
        }

>>>>>>> origin/main
    def _persist(self, run: WorkflowRun | None = None):
        if run is not None:
            self.repository.save_run(run)
        self.repository.save_metrics(self.metrics)

<<<<<<< HEAD
    # ------------------------------------------------------------------ lifecycle

    def create_run(self, scenario: str, requirement: str, requested_by: str = "system"):
=======
    def create_run(self, scenario: str, requirement: str) -> WorkflowRun:
>>>>>>> origin/main
        if scenario not in {"greenfield", "brownfield", "ambiguous"}:
            raise ValueError("scenario must be greenfield, brownfield, or ambiguous")
        if not requirement.strip():
            raise ValueError("requirement must not be empty")
<<<<<<< HEAD
        if not requested_by.strip():
            raise ValueError("requested_by is required")
=======
>>>>>>> origin/main
        run = WorkflowRun(
            str(uuid.uuid4()), scenario, requirement, build_plan(scenario, requirement)
        )
        run.context.update(
<<<<<<< HEAD
            {
                "run_id": run.id,
                "requirement": requirement,
                "scenario": scenario,
                "requested_by": requested_by,
                "outputs": {},
            }
        )
        run.record(
            "run_created", scenario=scenario, task_count=len(run.tasks), requested_by=requested_by
        )
=======
            {"run_id": run.id, "requirement": requirement, "scenario": scenario, "outputs": {}}
        )
        run.record("run_created", scenario=scenario, task_count=len(run.tasks))
>>>>>>> origin/main
        self.runs[run.id] = run
        self.metrics["runs"] += 1
        self._persist(run)
        return run

    def get_run(self, run_id: str) -> WorkflowRun:
        try:
            return self.runs[run_id]
        except KeyError as exc:
            raise WorkflowNotFound(run_id) from exc

    def _validate_graph(self, run: WorkflowRun):
        for task in run.tasks.values():
            for dep in task.depends_on:
                if dep not in run.tasks:
                    raise PolicyViolation(f"Unknown dependency {dep} for {task.id}")
        # Kahn's algorithm catches cycles before execution.
        remaining = {k: set(v.depends_on) for k, v in run.tasks.items()}
        ready = [k for k, deps in remaining.items() if not deps]
        visited = 0
        while ready:
            node = ready.pop()
            visited += 1
            for key, deps in remaining.items():
                if node in deps:
                    deps.remove(node)
                    if not deps:
                        ready.append(key)
        if visited != len(run.tasks):
            raise PolicyViolation("Workflow dependency graph contains a cycle")

<<<<<<< HEAD
    def _finalize(self, run: WorkflowRun, outcome: str, **details):
        """Move a run to a terminal state and count it exactly once per plan generation."""
        run.status = outcome
        run.completed_at = now_iso()
        if not run.context.get("terminal_metrics_recorded"):
            key = "rolled_back_runs" if outcome == "rolled_back" else outcome
            self.metrics[key] += 1
            self.metrics["total_execution_ms"] += run.context.get("execution_ms", 0.0)
            lead_ms = (_iso_to_epoch(run.completed_at) - _iso_to_epoch(run.started_at)) * 1000
            self.metrics["total_lead_time_ms"] += max(0.0, lead_ms)
            run.context["terminal_metrics_recorded"] = True
        run.record(f"run_{outcome}", **details)

    # ------------------------------------------------------------------ human input

=======
>>>>>>> origin/main
    def approve(self, run_id: str, task_id: str, approved: bool, approver: str, reason: str = ""):
        run = self.get_run(run_id)
        task = run.tasks.get(task_id)
        if not task:
            raise KeyError(task_id)
        if task.status != Status.WAITING_APPROVAL:
            raise ValueError("Task is not waiting for approval")
        if not approver.strip():
            raise ValueError("approver is required")
<<<<<<< HEAD
        # Separation of duties: the person who requested the change cannot approve it.
        requester = str(run.context.get("requested_by", "")).strip().lower()
        if approver.strip().lower() == requester:
            run.record("policy_violation", task_id, rule="self_approval", approver=approver)
            self._persist(run)
            raise ValueError("Requester cannot approve their own workflow")
        run.decisions.append(
            {
                "type": "approval",
=======
        run.decisions.append(
            {
>>>>>>> origin/main
                "task_id": task_id,
                "approved": approved,
                "approver": approver,
                "reason": reason,
                "generation": run.replan_count,
                "timestamp": now_iso(),
            }
        )
        run.record(
            "approval_decision", task_id, approved=approved, approver=approver, reason=reason
        )
        if approved:
            task.status = Status.READY
        else:
            task.status = Status.BLOCKED
            task.error = "Human approval denied"
<<<<<<< HEAD
            run.record("safe_stop", task_id, reason="approval_denied")
            self._finalize(run, "blocked", reason="approval_denied", task_id=task_id)
        self._persist(run)
        return run

    def clarify(self, run_id: str, answers: dict[str, str], answered_by: str):
        """Supply answers for a run paused at a clarification gate."""
        run = self.get_run(run_id)
        waiting = [t for t in run.tasks.values() if t.status == Status.WAITING_INPUT]
        if not waiting:
            raise ValueError("Run is not waiting for clarification")
        if not answered_by.strip():
            raise ValueError("answered_by is required")
        questions = run.context.get("human_questions", [])
        missing = [q for q in questions if not str(answers.get(q, "")).strip()]
        if missing:
            raise ValueError(f"Missing answers for: {missing}")
        unknown = sorted(set(answers) - set(questions))
        if unknown:
            raise ValueError(f"Answers supplied for unknown questions: {unknown}")
        self._record_clarifications(run, answers, answered_by)
        for task in waiting:
            task.status = Status.READY
        self._persist(run)
        return run

    def _record_clarifications(self, run: WorkflowRun, answers: dict[str, str], who: str):
        run.context["clarifications"] = dict(answers)
        run.context["clarified_by"] = who
        for question, answer in answers.items():
            run.decisions.append(
                {
                    "type": "clarification",
                    "question": question,
                    "answer": answer,
                    "answered_by": who,
                    "generation": run.replan_count,
                    "timestamp": now_iso(),
                }
            )
        run.record("clarification_received", answered_by=who, answer_count=len(answers))

    # ------------------------------------------------------------------ execution

    def _approved_task_ids(self, run: WorkflowRun) -> set[str]:
        # Only an approval made for the current plan generation is valid. Historical
        # approvals remain in the audit trail but cannot authorize a changed plan.
        return {
            d["task_id"]
            for d in run.decisions
            if d.get("type", "approval") == "approval"
            and d.get("approved")
            and d.get("generation", 0) == run.replan_count
        }

    def _upstream_evidence(self, run: WorkflowRun, task: Task) -> dict:
        """Summarize dependency outputs so an approver sees evidence, not just a task name."""
        evidence = {}
        for dep in task.depends_on:
            out = run.tasks[dep].output
            evidence[dep] = {
                k: out[k]
                for k in ("status", "passed", "exit_code", "findings", "artifact_path")
                if k in out
            }
        return evidence

    def _gate(self, run: WorkflowRun, task: Task, auto_approve: bool) -> bool:
        """Return True if the task may run now; otherwise park it at its gate."""
        if task.requires_input and "clarifications" not in run.context:
            if auto_approve:
                questions = run.context.get("human_questions", [])
                answers = {q: "DEMO ASSUMPTION: proceed with documented default" for q in questions}
                self._record_clarifications(run, answers, DEMO_APPROVER)
            else:
                task.status = Status.WAITING_INPUT
                run.record(
                    "clarification_requested",
                    task.id,
                    questions=run.context.get("human_questions", []),
                )
                return False
        if task.requires_approval and task.id not in self._approved_task_ids(run):
            if auto_approve:
                run.decisions.append(
                    {
                        "type": "approval",
                        "task_id": task.id,
                        "approved": True,
                        "approver": DEMO_APPROVER,
                        "reason": "explicit demo flag",
                        "generation": run.replan_count,
                        "timestamp": now_iso(),
                    }
                )
                run.record(
                    "approval_decision",
                    task.id,
                    approved=True,
                    approver=DEMO_APPROVER,
                    reason="explicit demo flag",
                )
            else:
                task.status = Status.WAITING_APPROVAL
                run.record(
                    "approval_requested",
                    task.id,
                    risk=task.risk,
                    description=task.description,
                    upstream_evidence=self._upstream_evidence(run, task),
                )
                return False
        return True

    async def execute(self, run_id: str, auto_approve: bool = False):
        run = self.get_run(run_id)
        async with self._lock(run_id):
            try:
                return await self._execute_locked(run, auto_approve)
            except PolicyViolation:
                raise
            except Exception as exc:
                self._interrupt(run, exc)
                raise ExecutionInterrupted(f"{type(exc).__name__}: {exc}") from exc

    def _interrupt(self, run: WorkflowRun, exc: Exception):
        """Leave the run resumable after an infrastructure failure (e.g. a DB write).

        Agent failures are handled per task; this covers failures of the engine itself.
        Without it the in-memory run stays 'running' forever, which also blocks
        rollback and replan until the process restarts.
        """
        for task in run.tasks.values():
            if task.status == Status.RUNNING:
                task.status = Status.READY
                task.error = "Interrupted by infrastructure failure; safe retry required"
        run.status = "interrupted"
        run.record("execution_interrupted", error=f"{type(exc).__name__}: {exc}")
        try:
            self._persist(run)
        except Exception:
            logger.exception("persist_failed_during_interrupt", extra={"run_id": run.id})

    async def _execute_locked(self, run: WorkflowRun, auto_approve: bool):
        # Terminal runs are immutable until explicitly replanned; repeated execute calls
        # must not double-count metrics or append duplicate completion events.
        if run.status in TERMINAL_RUN_STATES:
=======
            run.status = "blocked"
            run.record("safe_stop", task_id, reason="approval_denied")
        self._persist(run)
        return run

    async def execute(self, run_id: str, auto_approve: bool = False):
        run = self.get_run(run_id)
        # Terminal runs are immutable until explicitly replanned; repeated GET/execute
        # calls must not double-count metrics or append duplicate completion events.
        if run.status in {"succeeded", "failed", "blocked", "rolled_back"}:
>>>>>>> origin/main
            return run
        self._validate_graph(run)
        started = time.perf_counter()
        run.status = "running"
        run.record("execution_started")
        self._persist(run)
<<<<<<< HEAD
        paused_for = None
        while True:
            self._propagate_blocks(run)
            unfinished = [t for t in run.tasks.values() if t.status not in SETTLED_TASK_STATES]
            if not unfinished or all(t.status == Status.FAILED for t in unfinished):
                break
            ready = [
                t
                for t in unfinished
                if t.status in {Status.PENDING, Status.READY}
                and all(run.tasks[d].status == Status.SUCCEEDED for d in t.depends_on)
            ]
            executable = [t for t in ready if self._gate(run, t, auto_approve)]
            if not executable:
                waiting = {t.status for t in unfinished}
                if Status.WAITING_INPUT in waiting:
                    paused_for = "waiting_input"
                elif Status.WAITING_APPROVAL in waiting:
                    paused_for = "waiting_approval"
                else:
                    for t in unfinished:
                        if t.status in {Status.PENDING, Status.READY}:
                            t.status = Status.BLOCKED
                            t.error = "No executable dependency path"
                break
            for task in executable:
                task.status = Status.RUNNING
            self._persist(run)
            # Independent ready tasks run concurrently. Agents execute in worker threads so
            # blocking work (e.g. the pytest subprocess) neither serializes the branches
            # nor stalls the API server's event loop.
            await asyncio.gather(*(self._execute_task(run, task) for task in executable))
            self._persist(run)
            if run.status == "blocked":
                break

        elapsed = (time.perf_counter() - started) * 1000
        run.context["execution_ms"] = run.context.get("execution_ms", 0.0) + elapsed
        run.context["last_execution_latency_ms"] = round(elapsed, 2)
        if run.status == "blocked":
            self._finalize(run, "blocked", reason=run.context.get("blocked_reason"))
        elif paused_for:
            run.status = paused_for
        elif all(t.status == Status.SUCCEEDED for t in run.tasks.values()):
            self._finalize(run, "succeeded")
        else:
            self._finalize(
                run,
                "failed",
                failed=[t.id for t in run.tasks.values() if t.status == Status.FAILED],
                blocked=[t.id for t in run.tasks.values() if t.status == Status.BLOCKED],
            )
        self._persist(run)
        return run

    def _propagate_blocks(self, run: WorkflowRun):
        # Any failed dependency blocks its descendants; never silently skip the failure.
        changed = True
        while changed:
            changed = False
            for task in run.tasks.values():
                if task.status in {Status.PENDING, Status.READY} and any(
                    run.tasks[d].status in FAILED_TASK_STATES for d in task.depends_on
                ):
                    task.status = Status.BLOCKED
                    task.error = "Dependency did not succeed"
                    run.record("task_blocked", task.id, reason=task.error)
                    changed = True

    async def _execute_task(self, run: WorkflowRun, task: Task):
        task.attempts += 1
        run.record("task_started", task.id, attempt=task.attempts)
        # Agents get a snapshot of context, never the live object, so concurrent branches
        # cannot race on shared state. Outputs are merged back on the event loop.
        snapshot = copy.deepcopy(run.context)
        try:
            result = await asyncio.to_thread(self.agents.execute, task.id, snapshot)
        except Exception as exc:  # noqa: BLE001 - every agent failure must be recorded
            task.error = f"{type(exc).__name__}: {exc}"
            if task.first_failed_at is None:
                task.first_failed_at = time.time()
            run.record("task_attempt_failed", task.id, attempt=task.attempts, error=task.error)
            if not getattr(exc, "retryable", True):
                # A gate said no based on evidence. Retrying cannot change the answer.
                task.status = Status.BLOCKED
                run.status = "blocked"
                run.context["blocked_reason"] = task.error
                run.record("safe_stop", task.id, reason="gate_blocked", error=task.error)
            elif task.attempts <= task.max_retries:
                self.metrics["retries"] += 1
                run.record("retry_scheduled", task.id, next_attempt=task.attempts + 1)
                await asyncio.sleep(self.retry_backoff_seconds * (2 ** (task.attempts - 1)))
                task.status = Status.READY
=======
        while True:
            # Any failed dependency blocks its descendants; never silently skip the failure.
            changed = True
            while changed:
                changed = False
                for task in run.tasks.values():
                    if task.status in {Status.PENDING, Status.READY} and any(
                        run.tasks[d].status in {Status.FAILED, Status.BLOCKED, Status.ROLLED_BACK}
                        for d in task.depends_on
                    ):
                        task.status = Status.BLOCKED
                        task.error = "Dependency did not succeed"
                        run.record("task_blocked", task.id, reason=task.error)
                        changed = True

            unfinished = [
                t
                for t in run.tasks.values()
                if t.status
                not in {Status.SUCCEEDED, Status.SKIPPED, Status.BLOCKED, Status.ROLLED_BACK}
            ]
            if not unfinished:
                break

            ready = [
                t
                for t in unfinished
                if all(run.tasks[d].status == Status.SUCCEEDED for d in t.depends_on)
                and t.status in {Status.PENDING, Status.READY}
            ]
            if not ready:
                waiting = [t for t in unfinished if t.status == Status.WAITING_APPROVAL]
                if waiting:
                    run.status = "waiting_approval"
                    break
                if any(t.status == Status.RUNNING for t in unfinished):
                    await asyncio.sleep(0)
                    continue
                # Pending tasks with no executable path indicate a deadlock/invalid state.
                for t in unfinished:
                    if t.status in {Status.PENDING, Status.READY}:
                        t.status = Status.BLOCKED
                        t.error = "No executable dependency path"
                break

            # All ready tasks are independent at this point; execute them concurrently.
            executable = []
            for task in ready:
                # Only an approval made for the current plan generation is valid.
                # Historical approvals remain in the audit trail but cannot authorize
                # work after a replan changes the requirement.
                approved_task_ids = {
                    d["task_id"]
                    for d in run.decisions
                    if d.get("approved") and d.get("generation", 0) == run.replan_count
                }
                if task.requires_approval and not auto_approve and task.id not in approved_task_ids:
                    task.status = Status.WAITING_APPROVAL
                    run.record(
                        "approval_requested", task.id, risk=task.risk, description=task.description
                    )
                else:
                    if task.requires_approval and auto_approve:
                        run.decisions.append(
                            {
                                "task_id": task.id,
                                "approved": True,
                                "approver": "demo-auto-approval",
                                "reason": "explicit flag",
                                "generation": run.replan_count,
                                "timestamp": now_iso(),
                            }
                        )
                        run.record(
                            "approval_decision",
                            task.id,
                            approved=True,
                            approver="demo-auto-approval",
                            reason="explicit flag",
                        )
                    task.status = Status.RUNNING
                    executable.append(task)
            if not executable:
                run.status = "waiting_approval"
                break
            await asyncio.gather(*(self._execute_task(run, task) for task in executable))
            self._persist(run)

            # Re-plan signal: if upstream requirement changes, call replan() explicitly.
            if all(
                t.status in {Status.SUCCEEDED, Status.SKIPPED, Status.BLOCKED, Status.ROLLED_BACK}
                for t in run.tasks.values()
            ):
                break

        if all(t.status == Status.SUCCEEDED for t in run.tasks.values()):
            run.status = "succeeded"
            run.completed_at = now_iso()
            if not run.context.get("terminal_metrics_recorded"):
                self.metrics["succeeded"] += 1
                run.context["terminal_metrics_recorded"] = True
            run.record("run_succeeded")
        elif run.status != "waiting_approval" and run.status != "blocked":
            run.status = "failed"
            run.completed_at = now_iso()
            if not run.context.get("terminal_metrics_recorded"):
                self.metrics["failed"] += 1
                run.context["terminal_metrics_recorded"] = True
            run.record(
                "run_failed",
                blocked=[t.id for t in run.tasks.values() if t.status == Status.BLOCKED],
            )
        elapsed = (time.perf_counter() - started) * 1000
        self.metrics["total_latency_ms"] += elapsed
        run.context["last_execution_latency_ms"] = round(elapsed, 2)
        self._persist(run)
        return run

    async def _execute_task(self, run, task):
        task.attempts += 1
        run.record("task_started", task.id, attempt=task.attempts)
        try:
            # Bounded retry. Agent implementations should be idempotent or use idempotency keys.
            result = self.agents.execute(task.id, run.context)
            task.output = result
            task.status = Status.SUCCEEDED
            task.error = None
            run.context["outputs"][task.id] = result
            run.record("task_succeeded", task.id, attempt=task.attempts)
            self._persist(run)
         # Record unexpected agent failures and preserve retry handling.
        except Exception as exc:  # noqa: BLE001
            task.error = f"{type(exc).__name__}: {exc}"
            run.record("task_attempt_failed", task.id, attempt=task.attempts, error=task.error)
            if task.attempts <= task.max_retries:
                self.metrics["retries"] += 1
                task.status = Status.READY
                run.record("retry_scheduled", task.id, next_attempt=task.attempts + 1)
>>>>>>> origin/main
            else:
                task.status = Status.FAILED
                run.record("task_failed", task.id, error=task.error)
            self._persist(run)
<<<<<<< HEAD
            return

        task.output = result
        task.status = Status.SUCCEEDED
        task.error = None
        run.context["outputs"][task.id] = result
        if task.id == "understand" and result.get("human_questions"):
            run.context["human_questions"] = result["human_questions"]
        if task.first_failed_at is not None:
            recovery_ms = (time.time() - task.first_failed_at) * 1000
            self.metrics["recoveries"] += 1
            self.metrics["total_recovery_ms"] += recovery_ms
            run.record("task_recovered", task.id, recovery_ms=round(recovery_ms, 2))
            task.first_failed_at = None
        run.record("task_succeeded", task.id, attempt=task.attempts)
        self._persist(run)

    # ------------------------------------------------------------------ change control
=======
>>>>>>> origin/main

    def replan(self, run_id: str, new_requirement: str):
        """Explicitly replan when upstream requirements change; preserve decision/audit lineage."""
        run = self.get_run(run_id)
<<<<<<< HEAD
        if run.status == "running" or self._lock(run_id).locked():
=======
        if run.status == "running":
>>>>>>> origin/main
            raise ValueError("Cannot replan while execution is running")
        if not new_requirement.strip():
            raise ValueError("requirement must not be empty")
        old = run.requirement
        run.requirement = new_requirement
<<<<<<< HEAD
        run.replan_count += 1
        # Rebuild the plan from scratch for the new generation. Previous decisions and audit
        # events are retained as immutable lineage, but cannot authorize the new plan.
        run.tasks = build_plan(run.scenario, new_requirement)
        for key in (
            "terminal_metrics_recorded",
            "human_questions",
            "clarifications",
            "clarified_by",
            "blocked_reason",
            "execution_ms",
        ):
            run.context.pop(key, None)
        run.context["requirement"] = new_requirement
        run.context["outputs"] = {}
        run.status = "created"
        run.started_at = now_iso()
=======
        run.context["requirement"] = new_requirement
        run.replan_count += 1
        # Reset terminal accounting for the new plan generation, while retaining
        # previous decisions and audit events as immutable historical lineage.
        run.context.pop("terminal_metrics_recorded", None)
        # Invalidate downstream task outputs/status while preserving original decision lineage.
        for task in run.tasks.values():
            task.status = Status.PENDING
            task.attempts = 0
            task.output = {}
            task.error = None
        run.context["outputs"] = {}
        run.status = "created"
>>>>>>> origin/main
        run.completed_at = None
        run.record(
            "run_replanned",
            old_requirement=old,
            new_requirement=new_requirement,
            replan_count=run.replan_count,
        )
        self._persist(run)
        return run

    def rollback(self, run_id: str, reason: str, actor: str):
        """Safe-stop/compensating action for the prototype; no production deployment is performed."""
        run = self.get_run(run_id)
        if not actor.strip() or not reason.strip():
            raise ValueError("actor and reason are required")
<<<<<<< HEAD
        if run.status == "running" or self._lock(run_id).locked():
            raise ValueError("Cannot roll back while execution is running; wait or safe-stop")
        if run.status == "rolled_back":
            raise ValueError("Run is already rolled back")
        if not any(t.attempts for t in run.tasks.values()):
            raise ValueError("Nothing to roll back: no task has executed")
        reverted = []
        for task in run.tasks.values():
            if task.status == Status.SUCCEEDED and task.stage in {"implementation", "release"}:
                task.status = Status.ROLLED_BACK
                reverted.append(task.id)
        run.rollback_count += 1
        self.metrics["rollbacks"] += 1
        run.record("safe_stop", actor=actor, reason=reason)
        run.record(
            "rollback",
            actor=actor,
            reason=reason,
            rollback_count=run.rollback_count,
            reverted_tasks=reverted,
        )
        self._finalize(run, "rolled_back", actor=actor)
        self._persist(run)
        return run

    # ------------------------------------------------------------------ observability

    def metrics_snapshot(self):
        m = self.metrics
        terminal = m["succeeded"] + m["failed"] + m["blocked"]
        finished = terminal + m["rolled_back_runs"]

        def avg(total, count):
            return round(total / count, 2) if count else 0.0

        return {
            **m,
            "terminal_outcomes": terminal,
            # Fraction of finished plan generations that succeeded. Runs still in progress
            # or waiting for a human are excluded, so this is always within [0, 1].
            "success_rate": round(m["succeeded"] / terminal, 4) if terminal else 0.0,
            "average_execution_ms": avg(m["total_execution_ms"], finished),
            "average_lead_time_ms": avg(m["total_lead_time_ms"], finished),
            "mttr_ms": avg(m["total_recovery_ms"], m["recoveries"]),
            "retry_rate_per_run": avg(m["retries"], m["runs"]),
            "rollbacks_per_run": avg(m["rollbacks"], m["runs"]),
=======
        for task in run.tasks.values():
            if task.status == Status.SUCCEEDED and task.stage in {"implementation", "release"}:
                task.status = Status.ROLLED_BACK
        run.rollback_count += 1
        self.metrics["rollbacks"] += 1
        run.status = "rolled_back"
        run.completed_at = now_iso()
        run.record("safe_stop", actor=actor, reason=reason)
        run.record("rollback", actor=actor, reason=reason, rollback_count=run.rollback_count)
        self._persist(run)
        return run

    def metrics_snapshot(self):
        count = self.metrics["runs"]
        return {
            **self.metrics,
            "success_rate": round(self.metrics["succeeded"] / count, 4) if count else 0.0,
            "average_latency_ms": round(
                self.metrics["total_latency_ms"]
                / max(1, self.metrics["succeeded"] + self.metrics["failed"]),
                2,
            )
            if (self.metrics["succeeded"] + self.metrics["failed"])
            else 0.0,
>>>>>>> origin/main
        }
