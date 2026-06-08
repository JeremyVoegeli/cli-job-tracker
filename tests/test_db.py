"""Unit tests for jobs/db.py using a temporary file database."""

import pytest

from jobs import db


@pytest.fixture
def tmp_db(tmp_path):
    path = tmp_path / "test_jobs.db"
    db.init_db(path)
    return path


def _add(tmp_db, company="Acme", role="Engineer", date="2026-06-01", status="applied", notes=""):
    return db.add_application(company, role, date, status, notes, tmp_db)


# --- add_application ---

def test_add_returns_row_with_correct_fields(tmp_db):
    row = _add(tmp_db, company="Anthropic", role="SWE", date="2026-06-08", status="applied", notes="referral")
    assert row["company"] == "Anthropic"
    assert row["role"] == "SWE"
    assert row["date_applied"] == "2026-06-08"
    assert row["status"] == "applied"
    assert row["notes"] == "referral"
    assert row["id"] is not None
    assert row["created_at"] is not None
    assert row["updated_at"] is not None


def test_add_empty_notes_stored_as_null(tmp_db):
    row = _add(tmp_db, notes="")
    assert row["notes"] is None


def test_add_increments_id(tmp_db):
    a = _add(tmp_db)
    b = _add(tmp_db)
    assert b["id"] == a["id"] + 1


# --- list_applications ---

def test_list_empty(tmp_db):
    assert db.list_applications(path=tmp_db) == []


def test_list_returns_all_rows(tmp_db):
    _add(tmp_db)
    _add(tmp_db)
    assert len(db.list_applications(path=tmp_db)) == 2


def test_list_sorted_newest_date_first(tmp_db):
    _add(tmp_db, date="2026-05-01")
    _add(tmp_db, date="2026-06-15")
    _add(tmp_db, date="2026-06-01")
    rows = db.list_applications(path=tmp_db)
    dates = [r["date_applied"] for r in rows]
    assert dates == sorted(dates, reverse=True)


def test_list_filter_by_status_returns_only_matches(tmp_db):
    _add(tmp_db, company="A", status="applied")
    _add(tmp_db, company="B", status="interview")
    _add(tmp_db, company="C", status="interview")
    rows = db.list_applications(status="interview", path=tmp_db)
    assert len(rows) == 2
    assert all(r["status"] == "interview" for r in rows)


def test_list_filter_by_status_no_match_returns_empty(tmp_db):
    _add(tmp_db, status="applied")
    assert db.list_applications(status="offer", path=tmp_db) == []


# --- get_application ---

def test_get_returns_correct_row(tmp_db):
    added = _add(tmp_db, company="Corp")
    row = db.get_application(added["id"], path=tmp_db)
    assert row is not None
    assert row["company"] == "Corp"
    assert row["id"] == added["id"]


def test_get_unknown_id_returns_none(tmp_db):
    assert db.get_application(999, path=tmp_db) is None


# --- update_application ---

def test_update_status_changes_field(tmp_db):
    added = _add(tmp_db, status="applied")
    updated = db.update_application(added["id"], status="interview", path=tmp_db)
    assert updated["status"] == "interview"


def test_update_notes_changes_field(tmp_db):
    added = _add(tmp_db)
    updated = db.update_application(added["id"], notes="new note", path=tmp_db)
    assert updated["notes"] == "new note"


def test_update_touches_updated_at(tmp_db):
    added = _add(tmp_db)
    original = added["updated_at"]
    import time; time.sleep(1)
    updated = db.update_application(added["id"], status="offer", path=tmp_db)
    assert updated["updated_at"] >= original


def test_update_does_not_change_created_at(tmp_db):
    added = _add(tmp_db)
    updated = db.update_application(added["id"], status="offer", path=tmp_db)
    assert updated["created_at"] == added["created_at"]


def test_update_with_no_fields_returns_unchanged_row(tmp_db):
    added = _add(tmp_db)
    result = db.update_application(added["id"], path=tmp_db)
    assert result["status"] == added["status"]


def test_update_unknown_id_returns_none(tmp_db):
    assert db.update_application(999, status="offer", path=tmp_db) is None


# --- delete_application ---

def test_delete_returns_true_and_removes_row(tmp_db):
    added = _add(tmp_db)
    assert db.delete_application(added["id"], path=tmp_db) is True
    assert db.get_application(added["id"], path=tmp_db) is None


def test_delete_unknown_id_returns_false(tmp_db):
    assert db.delete_application(999, path=tmp_db) is False


def test_delete_does_not_affect_other_rows(tmp_db):
    a = _add(tmp_db)
    b = _add(tmp_db)
    db.delete_application(a["id"], path=tmp_db)
    assert db.get_application(b["id"], path=tmp_db) is not None
