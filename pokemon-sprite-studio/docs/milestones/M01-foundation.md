# M1 — Foundation & Desktop Application

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

A launchable Windows app: Tauri shell, React UI with all workspace routes, Python backend sidecar, SQLite via the existing migrations, app settings.

## Tasks

1. Scaffold `apps/desktop` (Tauri 2 + Vite + React + TS strict + Tailwind + Zustand).
2. Backend `api/`: FastAPI app factory, `/health`, `/version`; binds `127.0.0.1` on a port passed by Tauri; rejects requests without the per-launch bearer token.
3. `core/`: settings (pydantic-settings, `.env.example`), structured logging to `%APPDATA%\PSAS\logs`, typed domain errors, id generator (prefix + ULID), injectable clock.
4. `core/secrets.py`: `keyring` wrapper with get/set/delete per provider; never logs values.
5. Tauri side: spawn backend as sidecar (dev: `python -m backend.api`), wait for `/health`, kill on exit; show a friendly error screen if the backend fails to start.
6. Generate the TS API client from OpenAPI (`openapi-typescript`) via an npm script.
7. App shell: sidebar navigation for Dashboard, Generate, Sprite Editor, Animation Studio, Asset Library, Pokémon Database, Style Manager, Batch Production, Projects, Settings. Placeholder pages say what arrives in which milestone.
8. Settings page: data directory, theme, provider keys (write-only fields).

## Acceptance

- `npm run tauri dev` on Windows opens the app; backend health shows green.
- Closing the window leaves no orphan Python process.
- Request without token → 401 (test).
- Secret set via Settings is in Credential Manager, absent from logs/DB/files (test with keyring mocked + manual check).
- Backend tests and frontend Vitest suite pass.
