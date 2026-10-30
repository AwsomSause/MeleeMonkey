# Implementation Plan

Status legend: ⬜ not started · 🟨 in progress · ✅ complete (tests + manual acceptance + docs)

| # | Milestone | Status | Deliverable |
|---|---|---|---|
| M0 | Starter package | ✅ | Docs, DB schema, provider interface, design-spec schema, mock provider, tests |
| M1 | Foundation & desktop application | ⬜ | Launchable app |
| M2 | Asset library & project management | ⬜ | Functional asset manager |
| M3 | AI provider integration | ⬜ | Working generation pipeline |
| M4 | AI Director & concept generation | ⬜ | AI-assisted design studio |
| M5 | Battle sprite production | ⬜ | Static sprite workflow |
| M6 | Pixel processing engine | ⬜ | Game-ready image processing |
| M7 | Animation engine | ⬜ | Animated sprites |
| M8 | Integrated sprite editor | ⬜ | Editing studio |
| M9 | Overworld & additional asset types | ⬜ | Expanded asset support |
| M10 | Batch production | ⬜ | Bulk production |
| M11 | Export & game integration | ⬜ | Complete asset pipeline |
| M12 | Polish, optimization & release | ⬜ | Release candidate |

Each milestone has a self-contained prompt in `docs/milestones/`. Start a
Claude Code session with: *"Read CLAUDE.md, then execute
docs/milestones/M01-foundation.md."*

## Completion rules (every milestone)

- [ ] Scope documented in this file before coding starts
- [ ] Implementation works end to end
- [ ] Automated tests pass (`pytest`; frontend tests from M1)
- [ ] Manual acceptance steps run and recorded
- [ ] Demonstration steps written in the milestone section below
- [ ] Docs updated
- [ ] Known limitations listed
- [ ] Git checkpoint `M<n>: <summary>`

## First prototype gate (after M5)

Before M6 starts, this must work on a fresh install:

1. Create project, add species *Gardevoir*, attach references.
2. Generate concept variations (mock provider is acceptable for CI; one live
   provider for the manual run).
3. Approve one concept → it becomes a locked, very-high-priority reference.
4. Generate front and back battle sprites from the approved concept.
5. Approve both; create shiny via palette transform.
6. Quit and relaunch. References, versions, jobs, costs and history persist.

---

## M0 — Starter package ✅

**Delivered**
- `CLAUDE.md`, this plan, architecture/provider/animation/processing/data docs,
  decision log, twelve milestone prompts.
- `backend/database/migrations/0001_initial.sql` — full v1 schema covering all
  15 entities, plus migration bookkeeping.
- `backend/database/migrate.py` — forward-only migration runner.
- `backend/generation/providers/base.py` — provider contract, capability model,
  request/result models, typed errors.
- `backend/generation/providers/mock.py` — deterministic, free provider used
  by all routine tests.
- `backend/generation/caching/cache_key.py` — content-addressed cache keys.
- `backend/identity/design_spec.py` — versioned design specification schema
  (`schemas/design_spec.v1.json` is generated from it).
- Unit tests for all of the above.

**Known limitations**
- No desktop shell or UI yet (M1).
- No real provider adapters yet (M3).
- Budget enforcement is specified but not implemented (M3).
