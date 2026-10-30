# M3 — AI Provider Integration

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Real generation through at least two providers behind the existing contract, with a persistent job queue, budget guard, cache, and cost tracking.

## Tasks

1. Verify current capabilities/prices from vendor docs for the candidates in `docs/PROVIDERS.md`; record findings and `checked_on` dates.
2. Implement two adapters (recommend one hosted API + local SD-compatible API); HTTP mocked in tests; one `@live` smoke test each.
3. `orchestration/queue.py`: DB-backed queue, worker pool with per-provider concurrency, state machine from ARCHITECTURE, retries with backoff for `retryable` errors, cancel, pause, crash recovery on startup.
4. `orchestration/budget.py`: `BudgetGuard` per PROVIDERS.md; writes `provider_request` rows before and after each call (`sent` → `succeeded/failed/unknown`).
5. `caching/store.py`: lookup by `cache_key` before calling; "Regenerate" bypasses cache explicitly; cache hits recorded as `from_cache=1`, cost 0.
6. Provider selection modes (manual/recommended/economical/quality).
7. UI: Settings → Providers (keys, enable, test connection, budgets), job queue panel with live progress (SSE), spending view (estimated vs reported clearly labelled).
8. Provider comparison screen: same request to several providers, side-by-side.

## Acceptance

- With budget 0, no paid request is ever sent (test asserts adapter not called).
- Kill the backend mid-job; on restart the job is recovered (or flagged NEEDS_REVIEW if a charge may have occurred).
- Identical request twice → second served from cache, no provider call.
- Test suite makes zero network calls (enforce with a socket-blocking fixture).
