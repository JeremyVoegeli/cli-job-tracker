"""Unit tests for jobs/db.py using a temporary in-memory or temp-file database."""

import pytest

from jobs import db


@pytest.fixture
def tmp_db(tmp_path):
    """Return the path to a fresh temporary database, initialized with the schema."""
    path = tmp_path / "test_jobs.db"
    db.init_db(path)
    return path


def test_add_application_returns_row(tmp_db):
    """add_application should return a Row with the correct field values."""
    ...


def test_list_applications_empty(tmp_db):
    """list_applications should return an empty list when no rows exist."""
    ...


def test_list_applications_sorted_newest_first(tmp_db):
    """list_applications should return rows sorted by date_applied descending."""
    ...


def test_list_applications_filter_by_status(tmp_db):
    """list_applications with status= should only return matching rows."""
    ...


def test_get_application_found(tmp_db):
    """get_application should return the correct row for a known id."""
    ...


def test_get_application_not_found(tmp_db):
    """get_application should return None for an unknown id."""
    ...


def test_update_application_status(tmp_db):
    """update_application should change status and touch updated_at."""
    ...


def test_update_application_not_found(tmp_db):
    """update_application should return None for an unknown id."""
    ...


def test_delete_application_returns_true(tmp_db):
    """delete_application should return True and remove the row."""
    ...


def test_delete_application_not_found(tmp_db):
    """delete_application should return False for an unknown id."""
    ...
