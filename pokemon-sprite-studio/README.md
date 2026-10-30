# Pokémon Sprite & Animation Studio (PSAS)

A local-first Windows desktop studio for designing, generating, animating,
cleaning up and exporting Pokémon-style sprites. AI generation is optional and
pluggable. Project management, editing, previewing and exporting never require
a paid service.

> **Status: starter package (M0).** This folder holds the architecture, data
> model, provider contract, design-spec schema and milestone prompts, with
> tests. The desktop app itself starts at milestone M1.

## What's here

| Path | Contents |
|---|---|
| `CLAUDE.md` | Standing instructions for Claude Code |
| `IMPLEMENTATION_PLAN.md` | Milestone tracker and completion rules |
| `docs/ARCHITECTURE.md` | Processes, subsystems, folder layout, job lifecycle |
| `docs/PROVIDERS.md` | Provider contract, selection modes, benchmark, budget guard |
| `docs/IMAGE_PROCESSING.md` | Pixel pipeline stages and modes |
| `docs/ANIMATION_PIPELINE.md` | Templates, modes, consistency checks |
| `docs/DECISIONS.md` | Decision log |
| `docs/DEPENDENCIES.md` | Every dependency and why |
| `docs/milestones/M01…M12` | One self-contained Claude Code prompt per milestone |
| `backend/database/migrations/0001_initial.sql` | Full v1 SQLite schema |
| `backend/generation/providers/` | `ImageProvider` contract + free mock provider |
| `backend/generation/caching/cache_key.py` | Generation cache keys |
| `backend/identity/design_spec.py` | Versioned design spec (→ `schemas/design_spec.v1.json`) |
| `assets/` | Starter style preset and animation template |

## Running the tests

```bash
pip install -e ".[dev]"
pytest
ruff check backend tests
mypy
```

## Building it with Claude Code

Open a session in this folder and say:

> Read CLAUDE.md, then execute docs/milestones/M01-foundation.md.

Do one milestone per session (or several sessions per milestone). Check the
"Acceptance" section yourself before moving on.

## Legal note

This is a fan tool. It ships no official Pokémon artwork, and its fixtures and
presets are original. "Pokémon" is a trademark of Nintendo / Creatures /
GAME FREAK. Use a different name before distributing the app publicly.
