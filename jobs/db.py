"""SQLite persistence layer for the job tracker."""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".jobs_tracker.db"

VALID_STATUSES = {"applied", "interview", "offer", "rejected", "withdrawn"}


def get_db_path() -> Path:
    """Return the database path, respecting the DB_PATH environment variable."""
    ...


def get_connection(path: Path | None = None) -> sqlite3.Connection:
    """Open and return a sqlite3 connection with row_factory set to Row."""
    ...


def init_db(path: Path | None = None) -> None:
    """Create the applications table if it does not already exist."""
    ...


def add_application(
    company: str,
    role: str,
    date_applied: str,
    status: str,
    notes: str,
    path: Path | None = None,
) -> sqlite3.Row:
    """Insert a new application row and return it as a Row."""
    ...


def list_applications(
    status: str | None = None,
    path: Path | None = None,
) -> list[sqlite3.Row]:
    """Return all applications, newest date_applied first, optionally filtered by status."""
    ...


def get_application(id: int, path: Path | None = None) -> sqlite3.Row | None:
    """Return the application with the given id, or None if not found."""
    ...


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
    ...


def delete_application(id: int, path: Path | None = None) -> bool:
    """Delete the application with the given id.

    Returns True if a row was deleted, False if the id was not found.
    """
    ...
