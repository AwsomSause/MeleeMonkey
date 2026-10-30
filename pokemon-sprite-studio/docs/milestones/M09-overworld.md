# M9 — Overworld & Additional Asset Types

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Four-direction overworld sprites, icons and status animations.

## Tasks

1. Overworld workflow: down/up/left/right idle + walk (configurable tile size); right may be derived from left only if the user allows mirroring for that species.
2. Foot-placement and proportion checks across directions.
3. Optional run and special movement.
4. Icons: party/dex/menu sizes, palette-limited, optional 2-frame animation.
5. Status effect animations (template mode).
6. New asset types registered via a registry, not hardcoded switch statements.

## Acceptance

- Gardevoir overworld set with consistent foot line across all directions (automated check).
- Icons readable at native size (manual).
