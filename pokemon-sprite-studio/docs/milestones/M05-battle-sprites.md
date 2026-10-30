# M5 — Battle Sprite Production

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Front/back battle sprites, shiny variants and custom forms derived from approved identity.

## Tasks

1. Workflows per asset type (`generation/workflows/front_battle.py`, `back_battle.py`, …) built from approved concept + identity profile; back sprite is its own composition (never a mirror) and receives the approved front as a view-counterpart reference.
2. Canvas normalization shared between front and back (same scale factor, anchor bottom-centre); basic version until M6 replaces it.
3. Shiny: palette transform (D006) using an editable colour map; same map applied to front and back. Provider-edit alternative available.
4. Custom forms: any category string; inherits from parent; overrides shown as a diff from the parent spec.
5. Versioning: regeneration always creates a new version; approved versions untouched.

## Acceptance

Run the **first prototype gate** in IMPLEMENTATION_PLAN.md end to end (CI with mock provider, manual run with a live provider) and record results.
