# Architecture

## Process model

```
┌────────────────────────── Tauri 2 shell (Rust, thin) ──────────────────────────┐
│  React + TS UI (WebView2)          spawns + supervises                          │
│        │  HTTP/JSON + SSE           ───────────────────►  psas-backend sidecar  │
│        └──────────────────────────────────────────────►  (FastAPI, 127.0.0.1)  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

- The Rust side does three things only: launch/stop the backend sidecar, pass it
  a random port and a per-launch auth token, and expose native dialogs (file
  pickers, "reveal in Explorer"). No business logic in Rust.
- The backend is packaged with PyInstaller as a single executable and declared
  as a Tauri `externalBin` sidecar.
- Progress for long jobs is pushed to the UI with Server-Sent Events.
- The backend can run headless (`python -m backend.api`) for tests, scripting
  and a possible future web UI.

## Backend subsystems

| Package | Owns | Depends on |
|---|---|---|
| `api/` | HTTP routes, auth token check, request validation | all services (via interfaces) |
| `core/` | config, logging, errors, ids, clock, event bus | — |
| `database/` | connection, migrations, repositories | `core` |
| `storage/` | project folder layout, content hashing, file integrity, backup/restore | `core` |
| `projects/` | projects, species, forms, references, asset versions | `database`, `storage` |
| `identity/` | identity profiles, inheritance resolution, design-spec schema | `projects` |
| `generation/providers/` | one adapter per image provider | `core` only |
| `generation/prompts/` | template rendering from spec + style + view | `identity` |
| `generation/caching/` | cache keys, cache lookup/store | `storage` |
| `generation/orchestration/` | job queue, budget guard, provider selection | providers, caching, `database` |
| `director/` | Claude-based AI Director roles (optional) | `identity`, `generation` |
| `processing/` | background removal, scaling, palette, cleanup, validation | Pillow, OpenCV |
| `animation/` | templates, keyframe plans, transforms, assembly | `processing`, `generation` |
| `quality/` | technical QA, visual QA, scoring | `processing`, `director` (optional) |
| `export/` | PNG, GIF, sheets, JSON, engine profiles | `processing` |

Rules:
- Providers know nothing about species, projects or the database. They take a
  `GenerationRequest` and return a `GenerationResult`.
- `processing/` functions are pure: image(s) in, image(s) + report out. No DB.
- Only `orchestration/` decides *which* provider to call and whether money may
  be spent.
- The AI Director is optional. Every workflow must be completable manually
  without a Claude API key.

## Project folder on disk

```
<ProjectRoot>/
  project.psas.json          # project id, schema version, created_at
  psas.sqlite                # metadata
  references/<sha256>.png    # content-addressed, deduplicated
  generations/<job_id>/<n>.png   # raw provider output, immutable
  assets/<asset_id>/v<k>.png     # versioned processed outputs
  cache/<cache_key>.json     # pointer to generations/… + metadata
  exports/<export_id>/...
  backups/<timestamp>.zip
```

All paths stored in SQLite are relative to `<ProjectRoot>`, which makes
projects relocatable. Each file row stores its `sha256` so missing or moved
files can be detected and relinked.

## Job lifecycle

```
QUEUED → PREPARING → GENERATING → PROCESSING → QUALITY_CHECK → AWAITING_APPROVAL → APPROVED → EXPORTED
side states: PAUSED, NEEDS_REVIEW, FAILED, CANCELLED
```

The queue is the `generation_job` table, not memory. On startup, jobs in
`PREPARING/GENERATING/PROCESSING/QUALITY_CHECK` are reset to `QUEUED` (or to
`NEEDS_REVIEW` if the provider may already have charged — see
`provider_request.state`). Worker concurrency is configurable per provider.

## AI Director

A thin service around the Claude API with role-specific system prompts (Art
Director, Species Analyst, Form Designer, Sprite Artist, Animation Director,
Pixel Artist, QA Inspector). Every role returns JSON validated against a
Pydantic schema; free text is only used for explanations shown to the user.
The model ID is a setting, not a constant.

## Frontend

```
apps/desktop/src/
  pages/      one per workspace (Dashboard, Generate, SpriteEditor, AnimationStudio,
              AssetLibrary, PokemonDatabase, StyleManager, BatchProduction, Projects, Settings)
  components/ shared presentational components
  panels/     docked panels (AI Director, Layers, Palette, Timeline, References)
  editors/    canvas engine (pixel editor, onion skin, timeline)
  stores/     Zustand stores, one per domain
  api/        generated TypeScript client from FastAPI's OpenAPI schema
```

The TS client is generated (`openapi-typescript`) so request/response types
cannot drift from the backend.
