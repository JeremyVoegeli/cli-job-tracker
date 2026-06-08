"""CLI integration tests using Click's CliRunner and a temporary database."""

import pytest
from click.testing import CliRunner

from jobs.cli import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """Return a CliRunner and point DB_PATH at a fresh temp database."""
    db_path = str(tmp_path / "test_jobs.db")
    monkeypatch.setenv("DB_PATH", db_path)
    return CliRunner()


def test_add_creates_application(runner):
    """`jobs add` with valid interactive input should print the confirmation line."""
    ...


def test_list_empty(runner):
    """`jobs list` with no data should print 'No applications found.'"""
    ...


def test_list_shows_added_application(runner):
    """`jobs list` should display an application that was added via `jobs add`."""
    ...


def test_list_filter_by_status(runner):
    """`jobs list --status interview` should only show matching applications."""
    ...


def test_show_existing(runner):
    """`jobs show <id>` should print all fields for a known application."""
    ...


def test_show_unknown_id(runner):
    """`jobs show <id>` with an unknown id should print an error message."""
    ...


def test_update_status(runner):
    """`jobs update <id> --status interview` should update and confirm the change."""
    ...


def test_update_unknown_id(runner):
    """`jobs update <id>` with an unknown id should print an error message."""
    ...


def test_delete_confirmed(runner):
    """Confirming `jobs delete <id>` should remove the record."""
    ...


def test_delete_aborted(runner):
    """Declining `jobs delete <id>` should leave the record intact."""
    ...


def test_delete_unknown_id(runner):
    """`jobs delete <id>` with an unknown id should print an error message."""
    ...


def test_add_invalid_status(runner):
    """Providing an invalid status during `jobs add` should print an error."""
    ...
