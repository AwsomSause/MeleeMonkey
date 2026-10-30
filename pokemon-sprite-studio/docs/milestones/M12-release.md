# M12 — Polish, Optimization & Release

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Release candidate for Windows.

## Tasks

1. Performance: 1,000+ asset library benchmark, background workers, memory profile, lazy thumbnails.
2. Crash recovery and interrupted-job tests; backup/restore UX.
3. Package backend with PyInstaller as sidecar; Tauri MSI/NSIS installer; code-signing notes.
4. User guide (`docs/USER_GUIDE.md`) for non-programmers with screenshots.
5. Walk the release checklist (spec Part XIII) and record evidence for each item.

## Acceptance

- Fresh Windows VM: install, run the Gardevoir demo end to end, uninstall cleanly.
