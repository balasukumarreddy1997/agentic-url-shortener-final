<<<<<<< HEAD
import os
=======
>>>>>>> origin/main
from dataclasses import asdict
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

<<<<<<< HEAD
from orchestrator.engine import ExecutionInterrupted, WorkflowEngine, WorkflowNotFound
=======
from orchestrator.engine import WorkflowEngine, WorkflowNotFound
>>>>>>> origin/main

router = APIRouter(prefix="/api/workflows", tags=["agentic-workflows"])
engine = WorkflowEngine()


<<<<<<< HEAD
def demo_auto_approve_enabled() -> bool:
    """auto_approve bypasses every human gate, so it is off unless the operator opts in."""
    return os.getenv("ALLOW_DEMO_AUTO_APPROVE", "").strip().lower() in {"1", "true", "yes"}


class CreateWorkflowRequest(BaseModel):
    scenario: str = Field(pattern="^(greenfield|brownfield|ambiguous)$")
    requirement: str = Field(min_length=5, max_length=5000)
    requested_by: str = Field(min_length=1, max_length=100)
    auto_approve: bool = False


class ClarifyRequest(BaseModel):
    answers: dict[str, str] = Field(min_length=1)
    answered_by: str = Field(min_length=1, max_length=100)


=======
class CreateWorkflowRequest(BaseModel):
    scenario: str = Field(pattern="^(greenfield|brownfield|ambiguous)$")
    requirement: str = Field(min_length=5, max_length=5000)
    auto_approve: bool = False


>>>>>>> origin/main
class ApprovalRequest(BaseModel):
    approved: bool
    approver: str = Field(min_length=1, max_length=100)
    reason: str = Field(default="", max_length=1000)


class ReplanRequest(BaseModel):
    requirement: str = Field(min_length=5, max_length=5000)


class RollbackRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)
    actor: str = Field(min_length=1, max_length=100)


def serialize(value):
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {k: serialize(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    return value


@router.post("")
async def create_workflow(payload: CreateWorkflowRequest):
<<<<<<< HEAD
    if payload.auto_approve and not demo_auto_approve_enabled():
        raise HTTPException(
            status_code=403,
            detail="auto_approve is disabled; set ALLOW_DEMO_AUTO_APPROVE=1 for local demos only",
        )
    try:
        run = engine.create_run(payload.scenario, payload.requirement, payload.requested_by)
=======
    try:
        run = engine.create_run(payload.scenario, payload.requirement)
>>>>>>> origin/main
        run = await engine.execute(run.id, auto_approve=payload.auto_approve)
        return serialize(run)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
<<<<<<< HEAD
    except ExecutionInterrupted as exc:
        raise HTTPException(
            status_code=503, detail=f"Execution interrupted; resumable: {exc}"
        ) from exc
=======
>>>>>>> origin/main


@router.get("/{run_id}")
def get_workflow(run_id: str):
    try:
        return serialize(engine.get_run(run_id))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@router.post("/{run_id}/approve/{task_id}")
async def approve_workflow_task(run_id: str, task_id: str, payload: ApprovalRequest):
    try:
        engine.approve(run_id, task_id, payload.approved, payload.approver, payload.reason)
        return serialize(await engine.execute(run_id))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Task not found: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
<<<<<<< HEAD
    except ExecutionInterrupted as exc:
        raise HTTPException(
            status_code=503, detail=f"Execution interrupted; resumable: {exc}"
        ) from exc


@router.post("/{run_id}/clarify")
async def clarify_workflow(run_id: str, payload: ClarifyRequest):
    try:
        engine.clarify(run_id, payload.answers, payload.answered_by)
        return serialize(await engine.execute(run_id))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ExecutionInterrupted as exc:
        raise HTTPException(
            status_code=503, detail=f"Execution interrupted; resumable: {exc}"
        ) from exc
=======
>>>>>>> origin/main


@router.post("/{run_id}/replan")
def replan_workflow(run_id: str, payload: ReplanRequest):
    try:
        return serialize(engine.replan(run_id, payload.requirement))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{run_id}/rollback")
def rollback_workflow(run_id: str, payload: RollbackRequest):
    try:
        return serialize(engine.rollback(run_id, payload.reason, payload.actor))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
<<<<<<< HEAD
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{run_id}/resume")
async def resume_workflow(run_id: str):
    """Continue a run left 'interrupted' by an infrastructure failure or restart."""
    try:
        return serialize(await engine.execute(run_id))
    except WorkflowNotFound as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except ExecutionInterrupted as exc:
        raise HTTPException(
            status_code=503, detail=f"Execution interrupted; resumable: {exc}"
        ) from exc
=======
>>>>>>> origin/main


@router.get("/metrics/summary")
def workflow_metrics():
    return engine.metrics_snapshot()
