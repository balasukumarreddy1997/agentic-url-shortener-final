<<<<<<< HEAD
# Agentic Software Engineering System — URL Shortener

A FastAPI URL-shortening service plus a governed workflow orchestrator that drives an
engineering task through requirements, design, implementation, validation, documentation
and release, with human approval and clarification gates, audit lineage, bounded retries,
rollback and reliability metrics.

**Scope, stated plainly:** the workflow agents are deterministic local adapters, not LLM
agents. They inspect this repository, run its test suite in a subprocess, run behavioural
security checks against the real request schema, and write evidence artifacts. They do not
edit source code. The orchestration and governance layer is the focus of this prototype.
Start with the [engineering summary](DOCUMENTATION.md#1-engineering-summary); the
[risk table](DOCUMENTATION.md#9-risks-and-failure-scenarios) maps every failure scenario to
the test that proves its mitigation.

## Setup (Windows PowerShell)

Requires Python 3.11 or newer. From the repository root:

```powershell
=======
# Agentic Software Engineering System --- URL Shortener

A Python/FastAPI URL-shortening service paired with a governed,
auditable workflow-orchestration prototype.

## Overview

This repository contains two related components:

1.  **URL shortener API** --- create short links, redirect short codes,
    and retrieve basic analytics.
2.  **Governed workflow prototype** --- run engineering tasks with
    explicit states, approval gates, audit events, SQLite persistence,
    and recovery behavior.

The workflow adapters are deterministic local implementations. They
demonstrate orchestration and governance; they are not LLM agents and do
not autonomously rewrite application source code.

## Features

### URL shortener

-   Create a short code for a destination URL.
-   Redirect short URLs to their stored destination.
-   Retrieve analytics for a short code.
-   Persist URL data in SQLite.

### Workflow orchestration

-   Track workflow runs and task states.
-   Pause at configured human-approval gates.
-   Record decisions and audit events.
-   Persist workflow runs and aggregate metrics in SQLite.
-   Recover interrupted tasks marked `RUNNING` to a retryable `READY`
    state and record a recovery audit event.
-   Record safe-stop/rollback intent in the audit trail.

## Architecture

``` text
Client
  +--> FastAPI URL API --> URL repository --> SQLite
  +--> Orchestration API --> Workflow engine
                              +--> Deterministic task adapters
                              +--> Approval gates and decisions
                              +--> Audit trail
                              +--> SQLite workflow repository and metrics
```

## Requirements

Use the Python version and dependencies declared in `pyproject.toml`.
You need Python and pip; Git is needed for version control.

## Setup (Windows PowerShell)

Run from the repository root:

``` powershell
>>>>>>> origin/main
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e ".[dev]"
```

<<<<<<< HEAD
On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.

## Run the checks

```powershell
=======
If `pyproject.toml` does not define a `dev` extra, install the
development tools listed in that file separately.

If local configuration requires it, copy `.env.example` to `.env` and
edit it locally. Never commit `.env`.

## Run the API

Check the FastAPI application import path in `app/` and
`pyproject.toml`. If it is `app.main:app`, run:

``` powershell
py -m uvicorn app.main:app --reload
```

Open `/docs` on the running service to see the exact API schemas.

## API examples

### Create a short URL

`POST /api/shorten`

Example request (confirm the exact field name in `/docs`):

``` json
{
  "url": "https://example.com/articles/agentic-systems"
}
```

### Redirect

`GET /{short_code}`

A known short code redirects to its stored destination. Unknown-code
behavior is defined by the application.

### Analytics

`GET /api/analytics/{short_code}`

Returns the analytics fields implemented by the service. Consult `/docs`
for the exact response schema.

## Workflow lifecycle

At a high level, a run is created with tasks, eligible tasks are
executed by local deterministic adapters, status changes and audit
events are recorded, approval gates pause execution where required, and
the run reaches a terminal outcome.

The demonstrated end-to-end workflow included approval gates at
`implement_orchestrator` and `release_gate`. The exact task sequence is
defined by the orchestrator's configuration.

Workflow state and aggregate metrics persist in SQLite.
`WORKFLOW_DB_PATH` selects the workflow database and defaults to
`./workflow_state.db`. The URL database path is selected by
`DATABASE_PATH` and defaults to `./url_shortener.db`.

When a process restarts, tasks persisted as `RUNNING` are reset to
retryable `READY` state and an `execution_recovered` audit event is
recorded. This is not a distributed queue or an exactly-once execution
guarantee.

## Quality checks

``` powershell
>>>>>>> origin/main
py -m ruff check .
py -m pytest -q
```

<<<<<<< HEAD
Expected: Ruff reports no issues and pytest reports **58 passed**. Tests write only to a
temporary directory (see `tests/conftest.py`), never to the repository.

## Run the three scenarios end to end

```powershell
py scripts/run_scenarios.py
```

Runs greenfield, brownfield (with a mid-flight requirement change), ambiguous (with
clarification), and a fourth run where an injected security regression makes the release
gate fail closed. It uses the real agents, including the pytest subprocess, with distinct
named people as requester and approvers. Each run's task states, human decisions and full
audit trail are written to `docs/scenario-runs/`; the committed copies come from this
script.

## Run the service

```powershell
py -m uvicorn app.main:app --reload
```

Interactive API docs: http://127.0.0.1:8000/docs

## URL API

| Method | Path | Purpose | Responses |
|---|---|---|---|
| `POST` | `/api/shorten` | Create a short URL | 201, 409 custom code taken, 422 invalid/non-public URL or reserved code, 503 code space exhausted |
| `GET` | `/{code}` | Redirect to destination and record a click | 302, 404 |
| `GET` | `/api/urls/{code}/analytics` | Click count and timestamps | 200, 404 |
| `GET` | `/health` | Liveness | 200 |

```json
POST /api/shorten
{ "url": "https://example.com/articles/agentic-systems", "custom_code": "agentic" }
```

`custom_code` is optional (4–32 chars, `A-Z a-z 0-9 _ -`). Destinations must be public
`http`/`https` hosts: loopback, private, link-local (including cloud metadata
`169.254.169.254`), carrier-grade NAT, IPv4-mapped IPv6 and `.local`/`.internal` names are
rejected. Codes that collide with application routes (`docs`, `health`, …) are reserved.

## Workflow API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/workflows` | Create and start a run (`scenario`, `requirement`, `requested_by`) |
| `GET` | `/api/workflows/{run_id}` | Full run: tasks, context, decisions, audit trail |
| `POST` | `/api/workflows/{run_id}/clarify` | Answer open questions (`answers`, `answered_by`) |
| `POST` | `/api/workflows/{run_id}/approve/{task_id}` | Approve or deny a gate (`approved`, `approver`, `reason`) |
| `POST` | `/api/workflows/{run_id}/replan` | Change the requirement; rebuilds the plan, invalidates prior approvals |
| `POST` | `/api/workflows/{run_id}/rollback` | Safe-stop and roll back (`actor`, `reason`) |
| `POST` | `/api/workflows/{run_id}/resume` | Continue a run left `interrupted` by a crash or DB failure |
| `GET` | `/api/workflows/metrics/summary` | Success rate, retries, rollbacks, MTTR, latency |

### Walkthrough: ambiguous scenario with human control

```json
POST /api/workflows
{ "scenario": "ambiguous", "requirement": "make links short", "requested_by": "alice" }
```

1. The run returns `waiting_input` with `context.human_questions`. Design has not started.
2. `POST /clarify` with an answer for every question. The run proceeds and stops at
   `waiting_approval` on `implement_orchestrator` (high risk).
3. Approving as `alice` returns **409**: requesters cannot approve their own run.
   Approve as a different person.
4. Tests (a real pytest subprocess), security review and docs run; parallel branches
   execute concurrently. The run stops at `release_gate`, and the approval request in the
   audit trail carries the upstream evidence.
5. Approve `release_gate`. If any evidence is failing, the gate fails closed and the run
   ends `blocked`, not `succeeded`.

Use `"scenario": "greenfield"` or `"brownfield"` for the other two scenarios.

`auto_approve: true` bypasses every gate and is refused with **403** unless the server was
started with `ALLOW_DEMO_AUTO_APPROVE=1`. Auto-approvals are recorded under the approver
`demo-auto-approval` so they can never be mistaken for a human decision.

## Configuration

Set in the shell before starting the server; `.env` files are **not** loaded automatically.
`.env.example` lists every variable the code reads.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `./url_shortener.db` | URL and click data |
| `WORKFLOW_DB_PATH` | `./workflow_state.db` | Runs, audit, decisions, metrics |
| `AGENTIC_ARTIFACTS_DIR` | `<PROJECT_ROOT>/.agentic-artifacts` | Per-run evidence files |
| `PROJECT_ROOT` | current directory | Repository the agents inspect |
| `ALLOW_DEMO_AUTO_APPROVE` | unset (off) | Permit `auto_approve` |

## Repository layout

```text
app/            URL-shortener API, validation, service, SQLite store
orchestrator/   planner (DAG), engine (execution + governance), agents, persistence, API
scripts/        run_scenarios.py — end-to-end scenario runner
tests/          58 tests: API, validation, concurrency, orchestration, failure injection
docs/scenario-runs/  Real audit trails for each scenario
DOCUMENTATION.md     Engineering summary, requirements, assumptions, architecture,
                     scenarios, risk table, testing, trade-offs, limitations
SUBMISSION_STATUS.md Verified evidence and change log
AI_USAGE.md          How AI assistance was used
```

## Key limitations

No authentication (approver identity is self-asserted), no rate limiting, no URL
reputation checks, single-process orchestration state, and rollback reverts workflow state
but not source code or deployments. Full list and trade-offs in
[DOCUMENTATION.md](DOCUMENTATION.md#12-limitations).
=======
Previously verified in this project context: Ruff passed and pytest
reported 13 passing tests. A deprecation warning appeared but did not
fail the test run. Rerun the checks after any changes.

## Repository layout

``` text
.
├── app/                 # URL-shortener API
├── orchestrator/        # Workflow, agents/adapters, persistence, audit
├── tests/               # Automated tests
├── .env.example         # Example environment settings
├── .gitignore           # Excludes secrets, local state, and caches
├── pyproject.toml       # Project and tool configuration
├── README.md            # Overview and quick start
└── DOCUMENTATION.md     # Technical details and limitations
```

## Assumptions and limitations

-   SQLite keeps setup simple but is not a high-throughput,
    multi-instance production database strategy.
-   Workflow adapters are deterministic illustrative implementations;
    they do not modify source files.
-   Recovery makes interrupted tasks retryable but does not guarantee
    exactly-once side effects.
-   Retry handling is bounded and does not yet implement exponential
    backoff.
-   Metrics are prototype reliability counters, not production-grade SLO
    telemetry. MTTR is not derived from a complete incident lifecycle.
-   Rollback records intent/audit information; it does not revert a Git
    commit or deploy/rollback a production artifact.
-   Authentication/ownership, rate limiting, URL reputation checks,
    production observability, and load testing are not established as
    production-ready.

## Security and repository hygiene

Do not commit `.env`, credentials, local SQLite databases, cache
directories, or generated workflow artifacts. Treat submitted URLs as
untrusted input. Before public deployment, add suitable access controls,
abuse prevention, monitoring, URL safety protections, and operational
backups.

See [DOCUMENTATION.md](DOCUMENTATION.md) for component responsibilities,
workflow semantics, persistence, recovery, testing, and GitHub
publication guidance.
>>>>>>> origin/main
