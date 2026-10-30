-- PSAS schema v1. Never edit after commit; add 0002_*.sql instead.
-- Conventions: TEXT ids (prefix_ulid), ISO-8601 UTC timestamps, file paths
-- relative to the project root, JSON stored as TEXT and validated in Python.

CREATE TABLE project (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    default_style_profile_id TEXT REFERENCES style_profile(id),
    settings_json   TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE species (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    dex_number      INTEGER,                 -- NULL for original species
    is_original     INTEGER NOT NULL DEFAULT 0 CHECK (is_original IN (0, 1)),
    movement_classes_json TEXT NOT NULL DEFAULT '[]',  -- ["biped","floating",...]
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL,
    UNIQUE (project_id, name)
);

-- Forms are open-ended: category is free text ("shadow", "delta", "mega", ...).
CREATE TABLE form (
    id              TEXT PRIMARY KEY,
    species_id      TEXT NOT NULL REFERENCES species(id) ON DELETE CASCADE,
    parent_form_id  TEXT REFERENCES form(id),   -- NULL = base form
    slug            TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT 'base',
    created_at      TEXT NOT NULL,
    UNIQUE (species_id, slug)
);

-- Identity profiles are versioned; a form points at its current one.
CREATE TABLE identity_profile (
    id              TEXT PRIMARY KEY,
    form_id         TEXT NOT NULL REFERENCES form(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    spec_schema_version INTEGER NOT NULL,
    spec_json       TEXT NOT NULL,              -- DesignSpec (identity/design_spec.py)
    overrides_json  TEXT NOT NULL DEFAULT '{}', -- fields overriding the parent form
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'approved', 'superseded')),
    created_at      TEXT NOT NULL,
    UNIQUE (form_id, version)
);

CREATE TABLE reference_image (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    form_id         TEXT REFERENCES form(id) ON DELETE SET NULL,
    sha256          TEXT NOT NULL,
    path            TEXT NOT NULL,              -- references/<sha256>.png
    width           INTEGER NOT NULL,
    height          INTEGER NOT NULL,
    kind            TEXT NOT NULL CHECK (kind IN (
                        'approved_base_sprite', 'official_reference', 'approved_concept',
                        'view_counterpart', 'style_example', 'inspiration')),
    priority        INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 100),
    locked          INTEGER NOT NULL DEFAULT 0 CHECK (locked IN (0, 1)),
    group_name      TEXT,
    tags_json       TEXT NOT NULL DEFAULT '[]',
    allow_external_upload INTEGER NOT NULL DEFAULT 0 CHECK (allow_external_upload IN (0, 1)),
    replaced_by_id  TEXT REFERENCES reference_image(id),
    source_asset_version_id TEXT REFERENCES asset_version(id),
    created_at      TEXT NOT NULL
);
CREATE INDEX idx_reference_form ON reference_image(form_id);
CREATE INDEX idx_reference_sha ON reference_image(sha256);

CREATE TABLE style_profile (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    is_builtin      INTEGER NOT NULL DEFAULT 0 CHECK (is_builtin IN (0, 1)),
    config_json     TEXT NOT NULL,              -- resolution, palette, outline, shading...
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE provider (
    id              TEXT PRIMARY KEY,           -- 'mock', 'openai', 'flux', ...
    display_name    TEXT NOT NULL,
    enabled         INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    config_json     TEXT NOT NULL DEFAULT '{}', -- never contains secrets
    max_concurrency INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE generation_job (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    form_id         TEXT REFERENCES form(id),
    batch_id        TEXT REFERENCES batch(id),
    asset_type      TEXT NOT NULL,              -- front_battle, back_battle, concept, ...
    operation       TEXT NOT NULL CHECK (operation IN ('generate', 'edit', 'variations')),
    provider_id     TEXT REFERENCES provider(id),
    model           TEXT,
    state           TEXT NOT NULL CHECK (state IN (
                        'QUEUED', 'PREPARING', 'GENERATING', 'PROCESSING', 'QUALITY_CHECK',
                        'AWAITING_APPROVAL', 'APPROVED', 'EXPORTED',
                        'PAUSED', 'NEEDS_REVIEW', 'FAILED', 'CANCELLED')),
    request_json    TEXT NOT NULL,              -- full GenerationRequest
    cache_key       TEXT,
    attempts        INTEGER NOT NULL DEFAULT 0,
    max_attempts    INTEGER NOT NULL DEFAULT 3,
    progress        REAL NOT NULL DEFAULT 0,
    error           TEXT,
    estimated_cost_usd REAL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
CREATE INDEX idx_job_state ON generation_job(state);
CREATE INDEX idx_job_cache ON generation_job(cache_key);

-- One row per outbound provider call: the source of truth for spending.
CREATE TABLE provider_request (
    id              TEXT PRIMARY KEY,
    job_id          TEXT NOT NULL REFERENCES generation_job(id) ON DELETE CASCADE,
    provider_id     TEXT NOT NULL REFERENCES provider(id),
    state           TEXT NOT NULL CHECK (state IN ('sent', 'succeeded', 'failed', 'unknown')),
    from_cache      INTEGER NOT NULL DEFAULT 0 CHECK (from_cache IN (0, 1)),
    estimated_cost_usd REAL,
    actual_cost_usd REAL,                       -- NULL when provider does not report
    latency_ms      INTEGER,
    error           TEXT,
    created_at      TEXT NOT NULL
);
CREATE INDEX idx_provider_request_day ON provider_request(created_at);

CREATE TABLE generated_asset (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    form_id         TEXT REFERENCES form(id),
    asset_type      TEXT NOT NULL,
    style_profile_id TEXT REFERENCES style_profile(id),
    current_version_id TEXT REFERENCES asset_version(id),
    created_at      TEXT NOT NULL
);
CREATE INDEX idx_asset_form_type ON generated_asset(form_id, asset_type);

CREATE TABLE asset_version (
    id              TEXT PRIMARY KEY,
    asset_id        TEXT NOT NULL REFERENCES generated_asset(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    parent_version_id TEXT REFERENCES asset_version(id),
    generation_job_id TEXT REFERENCES generation_job(id),
    identity_profile_id TEXT REFERENCES identity_profile(id),
    raw_path        TEXT,                       -- immutable provider output
    path            TEXT NOT NULL,              -- processed output
    thumb_path      TEXT,
    sha256          TEXT NOT NULL,
    width           INTEGER NOT NULL,
    height          INTEGER NOT NULL,
    transparent     INTEGER NOT NULL CHECK (transparent IN (0, 1)),
    processing_json TEXT NOT NULL DEFAULT '{}',
    status          TEXT NOT NULL DEFAULT 'candidate'
                    CHECK (status IN ('candidate', 'approved', 'rejected', 'archived')),
    created_at      TEXT NOT NULL,
    UNIQUE (asset_id, version)
);

-- Approved versions are immutable: block edits to their files and status.
CREATE TRIGGER asset_version_approved_immutable
BEFORE UPDATE OF path, raw_path, sha256, width, height, status ON asset_version
WHEN OLD.status = 'approved' AND NOT (
     NEW.status IN ('approved', 'archived')
     AND NEW.path = OLD.path AND NEW.raw_path IS OLD.raw_path
     AND NEW.sha256 = OLD.sha256 AND NEW.width = OLD.width AND NEW.height = OLD.height)
BEGIN
    SELECT RAISE(ABORT, 'approved asset_version is immutable');
END;

CREATE TRIGGER asset_version_approved_undeletable
BEFORE DELETE ON asset_version
WHEN OLD.status = 'approved'
BEGIN
    SELECT RAISE(ABORT, 'approved asset_version cannot be deleted');
END;

CREATE TABLE animation_template (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    category        TEXT NOT NULL,              -- idle, physical_attack, faint, ...
    movement_classes_json TEXT NOT NULL DEFAULT '[]',
    definition_json TEXT NOT NULL,              -- keyframes, timing, paths, anchors, loop
    is_builtin      INTEGER NOT NULL DEFAULT 0 CHECK (is_builtin IN (0, 1)),
    created_at      TEXT NOT NULL
);

CREATE TABLE animation (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    form_id         TEXT NOT NULL REFERENCES form(id),
    base_asset_version_id TEXT NOT NULL REFERENCES asset_version(id),
    template_id     TEXT REFERENCES animation_template(id),
    name            TEXT NOT NULL,
    mode            TEXT NOT NULL CHECK (mode IN ('ai_keyframes', 'template', 'hybrid')),
    canvas_width    INTEGER NOT NULL,
    canvas_height   INTEGER NOT NULL,
    anchor_x        INTEGER NOT NULL,
    anchor_y        INTEGER NOT NULL,
    loop            INTEGER NOT NULL DEFAULT 1 CHECK (loop IN (0, 1)),
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'approved', 'archived')),
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE animation_frame (
    id              TEXT PRIMARY KEY,
    animation_id    TEXT NOT NULL REFERENCES animation(id) ON DELETE CASCADE,
    frame_index     INTEGER NOT NULL,
    duration_ms     INTEGER NOT NULL CHECK (duration_ms > 0),
    is_keyframe     INTEGER NOT NULL DEFAULT 0 CHECK (is_keyframe IN (0, 1)),
    source          TEXT NOT NULL CHECK (source IN ('ai', 'transform', 'manual', 'interpolated')),
    path            TEXT NOT NULL,
    sha256          TEXT NOT NULL,
    offset_x        INTEGER NOT NULL DEFAULT 0,
    offset_y        INTEGER NOT NULL DEFAULT 0,
    layers_json     TEXT NOT NULL DEFAULT '[]',
    status          TEXT NOT NULL DEFAULT 'candidate'
                    CHECK (status IN ('candidate', 'approved', 'rejected')),
    UNIQUE (animation_id, frame_index)
);

CREATE TABLE quality_report (
    id              TEXT PRIMARY KEY,
    asset_version_id TEXT REFERENCES asset_version(id) ON DELETE CASCADE,
    animation_id    TEXT REFERENCES animation(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL CHECK (kind IN ('technical', 'visual', 'animation', 'combined')),
    score           REAL,                       -- 0-100, NULL if not scored
    breakdown_json  TEXT NOT NULL DEFAULT '{}', -- per-category scores, N/A categories omitted
    issues_json     TEXT NOT NULL DEFAULT '[]', -- [{code, severity, message, auto}]
    created_at      TEXT NOT NULL,
    CHECK (asset_version_id IS NOT NULL OR animation_id IS NOT NULL)
);

CREATE TABLE batch (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    approval_mode   TEXT NOT NULL DEFAULT 'semi_automatic'
                    CHECK (approval_mode IN ('manual', 'semi_automatic', 'automatic', 'review_only')),
    state           TEXT NOT NULL DEFAULT 'draft'
                    CHECK (state IN ('draft', 'running', 'paused', 'completed', 'cancelled')),
    max_cost_usd    REAL,
    plan_json       TEXT NOT NULL,              -- species x deliverables matrix
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE export_job (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    profile         TEXT NOT NULL,              -- engine/export profile name
    options_json    TEXT NOT NULL DEFAULT '{}',
    state           TEXT NOT NULL CHECK (state IN ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED')),
    output_dir      TEXT,
    manifest_json   TEXT,
    error           TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE budget (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    daily_limit_usd REAL,
    monthly_limit_usd REAL,
    per_request_limit_usd REAL,
    max_variations  INTEGER NOT NULL DEFAULT 4
);
INSERT INTO budget (id) VALUES (1);
