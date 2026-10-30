# M8 — Integrated Sprite Editor

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Canvas pixel editor shared by sprite and animation workspaces.

## Tasks

1. Canvas engine in `editors/` (HTML canvas, integer zoom, pixel grid, pan).
2. Tools: pencil, eraser, fill, line, rectangle, eyedropper, rectangular/lasso selection, move, mirror.
3. Layers (add, delete, reorder, visibility, opacity), palette panel bound to the style profile.
4. Timeline: select, duplicate, delete, reorder, duration, onion skin (prev/next, configurable opacity), frame compare.
5. Command-pattern undo/redo with tests.
6. Save writes a new asset/frame version (manual source); never edits approved files.
7. Region marking for animation transforms.

## Acceptance

- Edit a sprite, undo/redo 50 steps, save → new version; original intact.
- Onion skin and timeline usable on a 10-frame animation at 60 fps.
