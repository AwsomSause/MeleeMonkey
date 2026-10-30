# Dependencies

Every dependency is listed with the reason it exists. Add a row before adding a package.

## Backend (Python)

| Package | Why | Since |
|---|---|---|
| pydantic | Typed models at every subsystem boundary; JSON Schema export | M0 |
| pillow | Image I/O and pixel manipulation | M0 |
| pytest, pytest-asyncio | Tests | M0 |
| jsonschema | Verifies exported JSON Schemas in tests | M0 |
| ruff, mypy | Lint and strict typing | M0 |
| fastapi, uvicorn | Local HTTP API (planned) | M1 |
| keyring | OS credential storage, i.e. Windows Credential Manager (planned) | M1 |
| httpx | Provider HTTP clients (planned) | M3 |
| anthropic | AI Director, optional (planned) | M4 |
| opencv-python-headless, numpy | Alignment, segmentation, analysis (planned) | M6 |
| pyinstaller | Package backend as Tauri sidecar (planned) | M12 |

## Frontend (planned, M1)

Tauri 2, React 18, TypeScript, Vite, Tailwind CSS, Zustand, openapi-typescript,
Vitest + Testing Library.

## Optional external tools

| Tool | Why | Required? |
|---|---|---|
| Aseprite CLI | `.aseprite` export | No (D002) |
| rembg | Better background removal | No |
