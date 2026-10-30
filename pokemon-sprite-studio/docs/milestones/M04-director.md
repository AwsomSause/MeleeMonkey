# M4 — AI Director & Concept Generation

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Optional Claude-powered director that turns natural language into validated DesignSpecs, builds prompts, scores candidates, and drives the approval loop.

## Tasks

1. Load the `claude-api` skill before writing Claude API code. Model ID comes from settings (`PSAS_DIRECTOR_MODEL`).
2. `director/` service with one module per role (Art Director, Species Analyst, Form Designer, Sprite Artist, Animation Director, Pixel Artist, QA Inspector). Each role: system prompt file in `generation/prompts/roles/`, structured JSON output validated by Pydantic, retry once on validation failure, then surface the error.
3. `generation/prompts/`: template renderer: DesignSpec + style profile + asset type + view + references → provider-specific prompt. Pure and unit-tested with snapshot tests.
4. Reference hierarchy applied when choosing which references to send (respect provider limit; highest priority and locked first).
5. Concept workflow: request → spec (user can edit as a form, not JSON) → N variations → optional director scoring → approve one → it becomes a very-high-priority locked reference and the form's identity profile is approved.
6. Generate workspace UI: left settings, centre candidates (zoom, checkerboard/solid background toggle, compare, approve/reject/regenerate), right collapsible AI Director panel with analysis, suggestions and history.
7. Everything must work without a Claude key (manual spec editing).

## Acceptance

- "Create a Shadow Gardevoir" → a valid spec with form `shadow` inheriting base identity.
- Director responses are mocked in tests; one `@live` test.
- Without a Claude key, the full concept flow works manually.
