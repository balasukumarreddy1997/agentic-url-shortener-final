"""SQLite persistence for workflow runs and aggregate counters."""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from orchestrator.models import AuditEvent, Status, Task, WorkflowRun


class WorkflowRepository:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("WORKFLOW_DB_PATH", "./workflow_state.db")
        self.initialize()

    def _connect(self):
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def initialize(self):
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS workflow_runs (run_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS workflow_metrics (singleton INTEGER PRIMARY KEY CHECK(singleton=1), payload TEXT NOT NULL)"
            )

    def save_run(self, run: WorkflowRun):
        payload = json.dumps(
            asdict(run), default=lambda obj: obj.value if isinstance(obj, Status) else str(obj)
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO workflow_runs(run_id,payload,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload, updated_at=CURRENT_TIMESTAMP",
                (run.id, payload),
            )

    def load_runs(self) -> dict[str, WorkflowRun]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM workflow_runs").fetchall()
        runs = {}
        for (payload,) in rows:
            data = json.loads(payload)
            tasks = {}
            for task_id, raw in data["tasks"].items():
                raw["status"] = Status(raw["status"])
                tasks[task_id] = Task(**raw)
            audit = [AuditEvent(**event) for event in data.get("audit", [])]
            run = WorkflowRun(
                id=data["id"],
                scenario=data["scenario"],
                requirement=data["requirement"],
                tasks=tasks,
                status=data.get("status", "created"),
                context=data.get("context", {}),
                decisions=data.get("decisions", []),
                audit=audit,
                created_at=data["created_at"],
                completed_at=data.get("completed_at"),
                replan_count=data.get("replan_count", 0),
                rollback_count=data.get("rollback_count", 0),
                started_at=data.get("started_at", data["created_at"]),
            )
            # A process may have died mid-task. Do not pretend that task completed;
            # make it retryable after restart and preserve the interruption in audit.
            interrupted = False
            for task in run.tasks.values():
                if task.status == Status.RUNNING:
                    task.status = Status.READY
                    task.error = "Recovered after process interruption; safe retry required"
                    interrupted = True
            if run.status == "running":
<<<<<<< HEAD
                run.status = "interrupted"
=======
                run.status = "created"
>>>>>>> origin/main
                interrupted = True
            if interrupted:
                run.record("execution_recovered", reason="previous process ended during execution")
            runs[run.id] = run
        return runs

    def save_metrics(self, metrics: dict[str, Any]):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO workflow_metrics(singleton,payload) VALUES(1,?) ON CONFLICT(singleton) DO UPDATE SET payload=excluded.payload",
                (json.dumps(metrics),),
            )

    def load_metrics(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM workflow_metrics WHERE singleton=1").fetchone()
        return json.loads(row[0]) if row else None
