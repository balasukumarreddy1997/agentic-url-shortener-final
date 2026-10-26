<<<<<<< HEAD
# Submission status

## Verified

Fresh virtualenv, `pip install -e ".[dev]"`, Python 3.12:

- `ruff check .`: clean.
- `pytest -q`: **58 passed**, with no files written to the repository.
- `scripts/run_scenarios.py`: greenfield, brownfield and ambiguous `succeeded`; the
  injected-failure run ended `blocked`. Reports are in `docs/scenario-runs/`.
- Live server smoke test (`uvicorn app.main:app`): shorten → 302 redirect → analytics
  count; ambiguous workflow paused at `waiting_input` → clarified → self-approval refused
  (409) → independent approvals → real pytest subprocess exit 0 → `succeeded`; `/health`
  stayed responsive; `auto_approve` without the demo flag refused (403).

## Changes from the previous revision

| Issue | Fix | Regression test |
|---|---|---|
| 4 of 13 tests failed on a clean install (`pytest-asyncio` missing) | Added to `dev` extras; `asyncio_mode = "auto"` | full suite on clean install |
| Release gate reported blockers but the run still `succeeded` | Gate raises `GateBlocked` (fail-closed, not retried); run ends `blocked` | `test_release_gate_fails_closed_on_blockers` |
| `success_rate` could reach 2.0 after replan | Final outcomes counted once per generation; rate = succeeded / final outcomes | `test_success_rate_never_exceeds_one_after_replan` |
| Public API `auto_approve` bypassed all gates | 403 unless `ALLOW_DEMO_AUTO_APPROVE` is set | `test_api_rejects_auto_approve_without_demo_flag` |
| Requester could approve their own run | `requested_by` required; self-approval refused and audited | `test_requester_cannot_self_approve` |
| "Parallel" branches ran one after another and blocked the server | Agents run via `asyncio.to_thread` on context snapshots | `test_parallel_branches_actually_overlap`, `test_event_loop_stays_responsive_during_agent_work` |
| Concurrent executions of one run could interleave | Per-run `asyncio.Lock` | `test_concurrent_execute_calls_are_serialized` |
| Ambiguous runs never paused for answers | `clarify` node and `waiting_input` state; `POST /clarify` | `test_ambiguous_run_pauses_for_clarification` |
| Custom-code race returned HTTP 500 | Insert first, map `IntegrityError` to 409 | `test_concurrent_custom_code_claims_yield_one_winner` |
| `docs`, `health` accepted as codes but unreachable | Reserved-code validation | `test_reserved_custom_codes_rejected` |
| Private, metadata, mapped-IPv6 and trailing-dot hosts accepted | `ipaddress`-based public-host policy | `test_reject_non_public_destinations` |
| Rollback allowed on never-run or already-rolled-back runs | State guards | `test_rollback_guards` |
| No MTTR; latency blended with human wait time | Task-level MTTR; separate execution time and lead time | `test_transient_failure_retries_and_records_mttr` |
| Retries had no backoff | Exponential backoff | `test_transient_failure_retries_and_records_mttr` |
| Security review searched for strings | Behavioural probes against the real schema | `test_security_agent_checks_real_repository_files` |
| Approvers saw only a task name | Approval requests include upstream evidence | `test_approval_request_carries_upstream_evidence` |
| A DB write failure left a run stuck `running` (no resume, rollback or replan) | New `interrupted` state; `POST /resume` | `test_db_failure_mid_run_leaves_run_resumable` |
| Analytics write failure turned a redirect into a 500 | Redirect proceeds; failure logged | `test_redirect_survives_analytics_write_failure` |
| Hung test suite, process crash and cyclic plans were untested | Failure-injection tests added | `test_hung_test_suite_times_out_and_fails_run`, `test_process_crash_mid_task_recovers_on_restart`, `test_cyclic_plan_is_rejected_before_execution` |
| No executable demo of the scenarios | `scripts/run_scenarios.py` writes real audit trails | — |
| Docs lacked an engineering summary, requirement normalization, assumptions and a risk analysis | Added to DOCUMENTATION.md §1–3 and §9 | — |
| Tests wrote databases and artifacts into the repo | `tests/conftest.py` isolates all paths | — |
| Docs listed a wrong analytics path and hedged wording | Rewritten from the code; `.env.example` lists only variables the code reads | — |

## Before submitting

- Fill in `AI_USAGE.md` with your own account; it is deliberately a template.
- Optionally rerun `py scripts/run_scenarios.py` so the reports carry your machine's
  timestamps.

## Not yet done (recommended next steps)

1. A real brownfield agent: generate a diff in a git worktree, test it there, apply only
   after approval; rollback discards the worktree.
2. An `impact_analysis` node for brownfield runs.
3. Selective re-planning: hash each task's output and invalidate only its descendants.
4. Authentication, so approver identity is verified rather than self-asserted.
5. A shared state store to support multiple workers.
6. Approval timeouts and escalation.
=======
# Submission status and verified evidence

## Verified in this revision
- `python -m pytest -q`: **13 tests passed**.
- Workflow engine persists run snapshots and metrics in SQLite and reloads run/task/decision/audit state after constructing a new engine against the same database.
- If a process restart finds a task marked `running`, the repository restores it to `ready` and records a recovery audit event rather than falsely claiming success.
- Workflow task handlers verify expected source modules exist and report their sizes.
- The workflow `tests` task invokes `python -m pytest -q tests/test_url_shortener.py --disable-warnings` with a timeout and records the actual exit code and output in `.agentic-artifacts/<run_id>/test-evidence.json`.
- Security-review task performs deterministic checks against the actual schema and SQL-store source files, then records residual risks in a JSON artifact.
- Documentation task verifies the README and submission status file exist and contain setup/test instructions.
- Manual end-to-end smoke run completed all eight workflow stages for greenfield, brownfield, and ambiguous scenarios using explicit `auto_approve=True`; each run captured passing focused-test evidence and reached the advisory release gate.
- Approval decisions from earlier plan generations cannot authorize work after replanning; repeated execution of a terminal run does not double-count success.

## Scope boundaries (do not overclaim)
- Agents are deterministic adapters, not LLM-based agents. Implementation-stage handlers inspect existing modules; they do not edit arbitrary application code automatically.
- The ambiguous scenario records questions but does not pause to collect a human answer before proceeding. This should be improved for a strict controlled-autonomy interpretation.
- The test workflow executes the focused URL-shortener tests, while the full suite is run separately by the operator.
- Security review is a deterministic source check, not a penetration test or compliance certification.
- Workflow metrics are persisted prototype counters, not complete production SLO/MTTR telemetry.
- Rollback is a safe-stop and audit record. It does not revert Git changes, undo database migrations, or reverse a deployed release.
- Authentication/authorization, rate limiting, abuse/phishing controls, load testing, backup/restore procedures, and production deployment are not implemented.
- Parallel task execution and retry behavior have basic implementation, but should receive more failure-injection and concurrency tests before production use.

## Recommended next improvements
1. Make ambiguous workflows pause for explicit clarification and record answers in decision lineage.
2. Add real, constrained repository-editing adapters that generate diffs, run tests, and require human approval before applying high-impact changes.
3. Add failure-injection tests for retry exhaustion, dependency blocking, concurrent persistence, and recovery after a mid-task process interruption.
4. Add authentication, authorization, rate limiting, stronger destination policy, and security testing.
5. Add production observability, SLOs, measured MTTR/latency, and backup/restore guidance.
>>>>>>> origin/main
