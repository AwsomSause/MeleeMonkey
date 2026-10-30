# M6 — Pixel Processing Engine

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Game-ready pixel art from raw generations, per docs/IMAGE_PROCESSING.md.

## Tasks

1. Implement each stage as a pure function with its own tests on fixture creatures.
2. Grid-aware downsampling; OKLab palette reduction with protected colours; palette mapping; outline inspection; cluster and alpha cleanup.
3. Preserve / Cleanup / Reconstruction modes; Cleanup default for generated assets; Reconstruction opt-in with before/after diff.
4. Pipeline runner records stages + params into `processing_json`; re-run with different settings creates a new version.
5. Technical QA checks produce `quality_report` rows.
6. Style Manager UI: create/edit style profiles (resolution, palette, outline, shading, cluster density, detail, framing, animation expectations). Ship built-in presets as original, word-described profiles (no ripped assets).
7. Visual regression tests: golden PNGs for each stage; diff on change.

## Acceptance

- 1024px mock "fake pixel art" fixture → 96×96 output with hard edges (no intermediate colours along edges beyond tolerance).
- Palette limit respected; outline/eye colours preserved.
- Raw generation file byte-identical after processing.
