"""Forward-only SQLite migration runner.

Migrations are ``NNNN_name.sql`` files applied in numeric order, each inside
its own transaction. Applied versions are recorded in ``schema_migrations``.
Callers are responsible for backing up the project before calling
:func:`migrate` on an existing database (see docs/DECISIONS.md D004).
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


@dataclass(frozen=True)
class Migration:
    version: int
    path: Path


def discover(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    found: list[Migration] = []
    for path in directory.glob("*.sql"):
        match = _NAME_RE.match(path.name)
        if match is None:
            raise ValueError(f"Badly named migration file: {path.name}")
        found.append(Migration(int(match.group(1)), path))
    found.sort(key=lambda m: m.version)
    versions = [m.version for m in found]
    if len(versions) != len(set(versions)):
        raise ValueError(f"Duplicate migration versions in {directory}")
    return found


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def current_version(conn: sqlite3.Connection) -> int:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def migrate(conn: sqlite3.Connection, directory: Path = MIGRATIONS_DIR) -> list[int]:
    """Apply pending migrations. Returns the versions applied."""
    applied: list[int] = []
    start = current_version(conn)
    for migration in discover(directory):
        if migration.version <= start:
            continue
        sql = migration.path.read_text(encoding="utf-8")
        try:
            conn.execute("BEGIN")
            # executescript would COMMIT implicitly; split statements ourselves
            # so the whole migration stays inside one transaction.
            for statement in _split_statements(sql):
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (migration.version, datetime.now(UTC).isoformat()),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        applied.append(migration.version)
    return applied


def _split_statements(sql: str) -> list[str]:
    """Split a script into complete statements, keeping trigger bodies intact."""
    statements: list[str] = []
    buffer = ""
    for line in sql.splitlines(keepends=True):
        if line.lstrip().startswith("--") and not buffer.strip():
            continue
        buffer += line
        if sqlite3.complete_statement(buffer):
            if buffer.strip():
                statements.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        raise ValueError(f"Incomplete SQL statement at end of migration: {buffer[:80]!r}")
    return statements
