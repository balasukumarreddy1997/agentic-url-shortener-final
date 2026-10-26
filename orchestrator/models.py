from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


class Status(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
<<<<<<< HEAD
    WAITING_INPUT = "waiting_input"
=======
>>>>>>> origin/main
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class Task:
    id: str
    stage: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    requires_approval: bool = False
<<<<<<< HEAD
    # A human must supply information (not just a yes/no) before this task can run.
    requires_input: bool = False
=======
>>>>>>> origin/main
    risk: str = "low"
    max_retries: int = 1
    status: Status = Status.PENDING
    attempts: int = 0
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
<<<<<<< HEAD
    # Wall-clock time (epoch seconds) of the first failed attempt in the current generation.
    # Used to measure time-to-recover when a later retry succeeds.
    first_failed_at: float | None = None
=======
>>>>>>> origin/main


@dataclass
class AuditEvent:
    timestamp: str
    run_id: str
    event: str
    task_id: str | None
    details: dict[str, Any]


@dataclass
class WorkflowRun:
    id: str
    scenario: str
    requirement: str
    tasks: dict[str, Task]
    status: str = "created"
    context: dict[str, Any] = field(default_factory=dict)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    audit: list[AuditEvent] = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)
    completed_at: str | None = None
    replan_count: int = 0
    rollback_count: int = 0
    started_at: str = field(default_factory=now_iso)

    def record(self, event: str, task_id: str | None = None, **details):
        self.audit.append(AuditEvent(now_iso(), self.id, event, task_id, details))
