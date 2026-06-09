"""SQLite persistence layer for the job tracker."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".jobs_tracker.db"

VALID_STATUSES = {"applied", "interview", "offer", "rejected", "withdrawn"}

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS applications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    company     TEXT    NOT NULL,
    role        TEXT    NOT NULL,
    date_applied TEXT   NOT NULL,
    status      TEXT    NOT NULL,
    notes       TEXT,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
)
"""


def get_db_path() -> Path:
    """Return the database path, respecting the DB_PATH environment variable."""
    env = os.environ.get("DB_PATH")
    return Path(env) if env else DEFAULT_DB_PATH


def get_connection(path: Path | None = None) -> sqlite3.Connection:
    """Open and return a sqlite3 connection with row_factory set to Row."""
    conn = sqlite3.connect(path or get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: Path | None = None) -> None:
    """Create the applications table if it does not already exist."""
    with get_connection(path) as conn:
        conn.execute(_CREATE_TABLE)


def add_application(
    company: str,
    role: str,
    date_applied: str,
    status: str,
    notes: str,
    path: Path | None = None,
) -> sqlite3.Row:
    """Insert a new application row and return it as a Row."""
    now = _now()
    with get_connection(path) as conn:
        cur = conn.execute(
            """
            INSERT INTO applications (company, role, date_applied, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (company, role, date_applied, status, notes or None, now, now),
        )
        row_id = cur.lastrowid
    return get_application(row_id, path)


def list_applications(
    status: str | None = None,
    path: Path | None = None,
) -> list[sqlite3.Row]:
    """Return all applications, newest date_applied first, optionally filtered by status."""
    with get_connection(path) as conn:
        if status is not None:
            rows = conn.execute(
                "SELECT * FROM applications WHERE status = ? ORDER BY date_applied DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM applications ORDER BY date_applied DESC"
            ).fetchall()
    return rows


def get_application(id: int, path: Path | None = None) -> sqlite3.Row | None:
    """Return the application with the given id, or None if not found."""
    with get_connection(path) as conn:
        return conn.execute(
            "SELECT * FROM applications WHERE id = ?", (id,)
        ).fetchone()


def update_application(
    id: int,
    status: str | None = None,
    notes: str | None = None,
    path: Path | None = None,
) -> sqlite3.Row | None:
    """Update status and/or notes on an application and return the updated row.

    Returns None if no application exists with the given id.
    Only provided (non-None) fields are updated.
    """
    if get_application(id, path) is None:
        return None

    fields: dict[str, str] = {"updated_at": _now()}
    if status is not None:
        fields["status"] = status
    if notes is not None:
        fields["notes"] = notes

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [id]

    with get_connection(path) as conn:
        conn.execute(
            f"UPDATE applications SET {set_clause} WHERE id = ?", values
        )

    return get_application(id, path)


def delete_application(id: int, path: Path | None = None) -> bool:
    """Delete the application with the given id.

    Returns True if a row was deleted, False if the id was not found.
    """
    with get_connection(path) as conn:
        cur = conn.execute("DELETE FROM applications WHERE id = ?", (id,))
    return cur.rowcount > 0


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
