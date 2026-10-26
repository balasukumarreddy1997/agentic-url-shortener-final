from orchestrator.models import Task


def build_plan(scenario: str, requirement: str) -> dict[str, Task]:
    """Create an explicit DAG. Architecture splits into parallel implementation/test/doc branches."""
    tasks = [
        Task(
            "understand", "requirements", "Normalize intent, assumptions, and acceptance criteria"
        ),
        Task(
            "design",
            "design",
            "Select components, API contracts, data model, and risk controls",
            ["understand"],
        ),
        Task(
            "implement_api",
            "implementation",
            "Implement URL APIs and persistence",
            ["design"],
            risk="medium",
        ),
        Task(
            "implement_orchestrator",
            "implementation",
            "Implement governed orchestration and scenario runner",
            ["design"],
            risk="high",
            requires_approval=True,
        ),
        Task(
            "tests",
            "validation",
            "Run unit and integration tests",
            ["implement_api", "implement_orchestrator"],
        ),
        Task(
            "security_review",
            "validation",
            "Review input validation, redirects, secrets, and policy controls",
            ["implement_api", "implement_orchestrator"],
        ),
        Task(
            "docs",
            "documentation",
            "Write architecture, setup, scenarios, and limitations",
            ["design"],
        ),
        Task(
            "release_gate",
            "release",
            "Aggregate test, security, and documentation evidence",
            ["tests", "security_review", "docs"],
            risk="high",
            requires_approval=True,
        ),
    ]
    if scenario == "brownfield":
        tasks[0].description += "; preserve existing contracts and identify impacted modules"
        tasks[1].description += "; plan a backward-compatible refactor"
    elif scenario == "ambiguous":
        tasks[0].description += "; list ambiguity and ask/record assumptions before implementation"
        tasks[0].output["assumptions_required"] = True
<<<<<<< HEAD
        # Design must not start until a human has answered the open questions. The
        # clarification gate is a distinct node so its answers enter decision lineage.
        tasks.insert(
            1,
            Task(
                "clarify",
                "requirements",
                "Collect human answers to open questions and record them as decisions",
                ["understand"],
                risk="medium",
                requires_input=True,
            ),
        )
        tasks[2].depends_on = ["clarify"]  # design
=======
>>>>>>> origin/main
    return {task.id: task for task in tasks}
