# M2 — Asset Library & Project Management

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Projects, species, forms, identity profiles, references and versioned assets — all persisted and searchable.

## Tasks

1. `storage/`: project folder layout (see ARCHITECTURE), content-addressed writes, sha256 integrity scan, missing-file detection and relink, project relocation, zip backup/restore. Automatic backup before migrations.
2. `projects/` repositories + services: CRUD for project/species/form; form inheritance (`parent_form_id`); identity profile versions; resolve effective spec = parent spec ⊕ overrides.
3. References: upload (dedupe by hash), kind, priority (defaults from the reference hierarchy table: approved sprite/official/approved concept 90, counterpart 70, style 50, inspiration 20), lock, group, tags, replace (keeps history), `allow_external_upload` default off.
4. Assets: create version, approve (becomes a locked reference), reject, archive. Approval is the only path into `approved`; DB triggers already block mutation.
5. Thumbnails (256px max, nearest-neighbour) generated on write.
6. API routes + UI: Projects page, Pokémon Database (species/forms tree), reference manager, Asset Library grid with filters (species, form, type, status, style, provider, date, score) and asset detail page with version history.
7. Fixtures: draw original test creatures (biped, quadruped, flyer, floater, serpentine, insectoid, heavy, high-detail) as small PNGs in `tests/fixtures/creatures/`.

## Acceptance

- Create project → species → form → upload references → quit → relaunch → everything is there.
- Move the project folder; reopening relinks with no data loss.
- Attempt to delete an approved version via API → refused with a clear message.
- Library with 1,000 seeded assets scrolls smoothly (virtualized grid; thumbnails only).
