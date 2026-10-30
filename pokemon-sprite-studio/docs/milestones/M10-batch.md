# M10 — Batch Production

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Bulk generation with approvals, spending limits and pause/resume.

## Tasks

1. Import CSV/JSON and dex-range selection → species × deliverables matrix editor.
2. Batch planner orders work concept → views → variants → animations (cost-saving workflow) and estimates total cost up front.
3. Approval modes (manual, semi-automatic default, automatic with QA thresholds, review-only). An unapproved concept can never become a batch reference (enforce in code + test).
4. Pause/resume/cancel; automatic retries; batch-level max cost.
5. Batch approval UI (grid, keyboard shortcuts) and batch export.

## Acceptance

- 20-species mock batch: pause midway, restart app, resume; no duplicate provider calls.
- Batch stops before exceeding max cost.
