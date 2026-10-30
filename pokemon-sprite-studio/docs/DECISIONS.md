# Decision Log

Append-only. To change a decision, add a new entry that supersedes it.

## D001 — Backend as Tauri sidecar over localhost HTTP
Keeps Python independent of the UI (spec requirement), allows headless use and
tests, and avoids embedding Python in Rust. The backend binds to `127.0.0.1`
on a random port with a per-launch bearer token so other local software cannot
drive it.

## D002 — Aseprite CLI is optional, not required
Aseprite is paid software. The spec forbids requiring payment for basic
exporting, so sprite sheets, GIFs and JSON are produced natively with Pillow.
If the user configures an Aseprite path, `.aseprite` export becomes available.

## D003 — API keys via `keyring`
`keyring` uses Windows Credential Manager on Windows. Keys are read by the
backend only; the frontend sends a key once during setup and never receives
it back.

## D004 — Forward-only SQL migrations, plus backups
SQLite cannot reliably reverse every schema change. Instead: numbered forward
migrations, and an automatic project backup before any migration runs. This
satisfies "reversible where possible" with a guaranteed restore path.

## D005 — Content-addressed reference and cache storage
References are stored by SHA-256, so duplicate uploads cost nothing and cache
keys can reference image content rather than file names.

## D006 — Shiny variants default to palette transformation
Recolouring an approved sprite deterministically is free and preserves the
design exactly. Provider-based editing is offered as an alternative.

## D007 — Original test creatures only
Test fixtures are original creatures drawn for the project (one per body plan:
biped, quadruped, flyer, floater, serpentine, insectoid, heavy, high-detail).
No official artwork is committed.

## D008 — Hybrid animation is the default mode
AI provides key poses; deterministic transforms handle timing, anchoring and
in-betweens. Pure template mode is the free fallback; pure AI-keyframe mode
is opt-in.
