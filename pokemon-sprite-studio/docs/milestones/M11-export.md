# M11 — Export & Game Integration

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Validated exports for games.

## Tasks

1. PNG (single/frames), GIF (correct durations, transparency), sprite sheets (grid/packed, padding, power-of-two option) with JSON atlas.
2. Export profiles (folder layout + naming + metadata format) — include a generic profile and one for a browser-game layout; profiles are user-editable JSON.
3. Optional Aseprite CLI export (D002).
4. Export validation (files open, dimensions, frame counts, atlas references valid) recorded in `export_job.manifest_json`.
5. Export never includes secrets or private notes.

## Acceptance

- Export Gardevoir pack; re-import the atlas in a test and verify every frame rect.
