"""CLI integration tests using Click's CliRunner and a temporary database."""

from datetime import date

import pytest
from click.testing import CliRunner

from jobs.cli import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """Return a CliRunner pointed at a fresh temp database."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test_jobs.db"))
    return CliRunner()


def _add(runner, company="Acme", role="Engineer", date_applied="2026-06-01",
         status="applied", notes=""):
    """Helper: invoke `jobs add` with pre-set answers."""
    return runner.invoke(
        cli, ["add"],
        input=f"{company}\n{role}\n{date_applied}\n{status}\n{notes}\n",
    )


# --- jobs add ---

def test_add_confirmation_message(runner):
    result = _add(runner, company="Anthropic", role="Software Engineer",
                  date_applied="2026-06-08", status="applied", notes="referral")
    assert result.exit_code == 0
    assert "Added application #1" in result.output
    assert "Anthropic" in result.output
    assert "Software Engineer" in result.output
    assert "applied" in result.output


def test_add_persists_to_db(runner, tmp_path, monkeypatch):
    from jobs import db
    db_path = tmp_path / "test_jobs.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    runner2 = CliRunner()
    _add(runner2, company="Globex", role="Dev", date_applied="2026-06-01")
    rows = db.list_applications(path=db_path)
    assert len(rows) == 1
    assert rows[0]["company"] == "Globex"


def test_add_default_status_is_applied(runner):
    # Hit enter to accept the "applied" default for status
    result = runner.invoke(cli, ["add"], input="Corp\nDev\n2026-06-01\n\n\n")
    assert result.exit_code == 0
    assert "applied" in result.output


def test_add_default_date_is_today(runner):
    today = date.today().isoformat()
    result = runner.invoke(cli, ["add"], input="Corp\nDev\n\napplied\n\n")
    assert result.exit_code == 0
    assert today in result.output


def test_add_empty_notes_accepted(runner):
    result = _add(runner, notes="")
    assert result.exit_code == 0


def test_add_invalid_status_prints_error(runner):
    result = runner.invoke(cli, ["add"], input="Corp\nDev\n2026-06-01\nbogus\n\n")
    assert result.exit_code != 0
    assert "Invalid status 'bogus'" in result.output
    assert "applied" in result.output  # valid options listed


def test_add_status_is_case_insensitive(runner):
    result = _add(runner, status="INTERVIEW")
    assert result.exit_code == 0
    assert "interview" in result.output


def test_add_second_application_gets_next_id(runner):
    _add(runner)
    result = _add(runner)
    assert "Added application #2" in result.output


# --- jobs list ---

def test_list_empty_prints_message(runner):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No applications found." in result.output


def test_list_shows_header_row(runner):
    _add(runner)
    result = runner.invoke(cli, ["list"])
    assert "ID" in result.output
    assert "Company" in result.output
    assert "Role" in result.output
    assert "Status" in result.output
    assert "Date Applied" in result.output


def test_list_shows_added_application(runner):
    _add(runner, company="Anthropic", role="Software Engineer",
         date_applied="2026-06-08", status="applied")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Anthropic" in result.output
    assert "Software Engineer" in result.output
    assert "applied" in result.output
    assert "2026-06-08" in result.output


def test_list_sorted_newest_date_first(runner):
    _add(runner, company="Old Co", date_applied="2026-05-01")
    _add(runner, company="New Co", date_applied="2026-06-15")
    result = runner.invoke(cli, ["list"])
    assert result.output.index("New Co") < result.output.index("Old Co")


def test_list_multiple_rows_all_appear(runner):
    _add(runner, company="Alpha")
    _add(runner, company="Beta")
    _add(runner, company="Gamma")
    result = runner.invoke(cli, ["list"])
    assert "Alpha" in result.output
    assert "Beta" in result.output
    assert "Gamma" in result.output


def test_list_filter_by_status_shows_only_matches(runner):
    _add(runner, company="ApplyOnly", status="applied")
    _add(runner, company="InterviewOne", status="interview")
    _add(runner, company="InterviewTwo", status="interview")
    result = runner.invoke(cli, ["list", "--status", "interview"])
    assert result.exit_code == 0
    assert "InterviewOne" in result.output
    assert "InterviewTwo" in result.output
    assert "ApplyOnly" not in result.output


def test_list_filter_no_matches_prints_message(runner):
    _add(runner, status="applied")
    result = runner.invoke(cli, ["list", "--status", "offer"])
    assert result.exit_code == 0
    assert "No applications found." in result.output


def test_list_filter_is_case_insensitive(runner):
    _add(runner, company="Corp", status="interview")
    result = runner.invoke(cli, ["list", "--status", "INTERVIEW"])
    assert result.exit_code == 0
    assert "Corp" in result.output


# --- stubs for commands not yet implemented ---

def test_show_existing(runner): ...
def test_show_unknown_id(runner): ...
def test_update_status(runner): ...
def test_update_unknown_id(runner): ...
def test_delete_confirmed(runner): ...
def test_delete_aborted(runner): ...
def test_delete_unknown_id(runner): ...
