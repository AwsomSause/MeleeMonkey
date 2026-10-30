import sqlite3
from pathlib import Path

import pytest

from backend.database.migrate import connect, current_version, discover, migrate

EXPECTED_TABLES = {
    "project", "species", "form", "identity_profile", "reference_image", "style_profile",
    "generation_job", "provider_request", "generated_asset", "asset_version",
    "animation", "animation_frame", "animation_template", "export_job", "provider",
    "quality_report", "batch", "budget", "schema_migrations",
}
NOW = "2026-10-30T00:00:00+00:00"


@pytest.fixture
def db(tmp_path: Path) -> sqlite3.Connection:
    conn = connect(tmp_path / "psas.sqlite")
    migrate(conn)
    return conn


def test_all_entities_created(db: sqlite3.Connection) -> None:
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert EXPECTED_TABLES <= tables


def test_migrate_is_idempotent(db: sqlite3.Connection) -> None:
    latest = discover()[-1].version
    assert current_version(db) == latest
    assert migrate(db) == []


def test_foreign_keys_enforced(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO species (id, project_id, name, created_at) VALUES ('s1', 'nope', 'X', ?)",
            (NOW,),
        )


def _seed_approved_version(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO project (id, name, created_at, updated_at) VALUES ('p', 'P', ?, ?)",
               (NOW, NOW))
    db.execute("INSERT INTO generated_asset (id, project_id, asset_type, created_at) "
               "VALUES ('a', 'p', 'front_battle', ?)", (NOW,))
    db.execute(
        "INSERT INTO asset_version (id, asset_id, version, path, sha256, width, height, "
        "transparent, status, created_at) "
        "VALUES ('v1', 'a', 1, 'assets/a/v1.png', 'abc', 96, 96, 1, 'approved', ?)",
        (NOW,),
    )


def test_approved_version_cannot_be_overwritten(db: sqlite3.Connection) -> None:
    _seed_approved_version(db)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        db.execute("UPDATE asset_version SET path = 'other.png' WHERE id = 'v1'")
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        db.execute("UPDATE asset_version SET status = 'candidate' WHERE id = 'v1'")


def test_approved_version_cannot_be_deleted(db: sqlite3.Connection) -> None:
    _seed_approved_version(db)
    with pytest.raises(sqlite3.IntegrityError, match="cannot be deleted"):
        db.execute("DELETE FROM asset_version WHERE id = 'v1'")


def test_approved_version_can_be_archived(db: sqlite3.Connection) -> None:
    _seed_approved_version(db)
    db.execute("UPDATE asset_version SET status = 'archived' WHERE id = 'v1'")
    assert db.execute("SELECT status FROM asset_version").fetchone()[0] == "archived"


def test_failed_migration_rolls_back(tmp_path: Path) -> None:
    mig_dir = tmp_path / "migs"
    mig_dir.mkdir()
    (mig_dir / "0001_ok.sql").write_text("CREATE TABLE a (x INTEGER);")
    (mig_dir / "0002_bad.sql").write_text("CREATE TABLE b (x INTEGER);\nNOT VALID SQL;")
    conn = connect(tmp_path / "t.sqlite")
    with pytest.raises(sqlite3.OperationalError):
        migrate(conn, mig_dir)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "a" in tables and "b" not in tables
    assert current_version(conn) == 1
