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


# --- jobs show ---

def test_show_prints_all_fields(runner):
    _add(runner, company="Anthropic", role="Software Engineer",
         date_applied="2026-06-08", status="applied", notes="referral")
    result = runner.invoke(cli, ["show", "1"])
    assert result.exit_code == 0
    assert "Anthropic" in result.output
    assert "Software Engineer" in result.output
    assert "applied" in result.output
    assert "2026-06-08" in result.output
    assert "referral" in result.output
    assert "Created" in result.output
    assert "Updated" in result.output


def test_show_labels_present(runner):
    _add(runner)
    result = runner.invoke(cli, ["show", "1"])
    for label in ("ID:", "Company:", "Role:", "Status:", "Date Applied:", "Notes:", "Created:", "Updated:"):
        assert label in result.output


def test_show_empty_notes_does_not_error(runner):
    _add(runner, notes="")
    result = runner.invoke(cli, ["show", "1"])
    assert result.exit_code == 0
    assert "Notes:" in result.output


def test_show_unknown_id_prints_error(runner):
    result = runner.invoke(cli, ["show", "999"])
    assert result.exit_code != 0
    assert "No application found with ID 999" in result.output


def test_show_unknown_id_after_add(runner):
    _add(runner)
    result = runner.invoke(cli, ["show", "99"])
    assert result.exit_code != 0
    assert "No application found with ID 99" in result.output

# --- jobs update ---

def test_update_status_changes_status(runner):
    _add(runner, company="Anthropic", role="SWE", status="applied")
    result = runner.invoke(cli, ["update", "1", "--status", "interview"])
    assert result.exit_code == 0
    assert "Updated application #1" in result.output
    assert "Anthropic" in result.output
    assert "SWE" in result.output
    assert "interview" in result.output


def test_update_notes_replaces_notes(runner):
    _add(runner, notes="old note")
    result = runner.invoke(cli, ["update", "1", "--notes", "new note"])
    assert result.exit_code == 0
    # verify the change was persisted
    show = runner.invoke(cli, ["show", "1"])
    assert "new note" in show.output
    assert "old note" not in show.output


def test_update_both_options_at_once(runner):
    _add(runner, status="applied", notes="first")
    result = runner.invoke(cli, ["update", "1", "--status", "offer", "--notes", "second"])
    assert result.exit_code == 0
    show = runner.invoke(cli, ["show", "1"])
    assert "offer" in show.output
    assert "second" in show.output


def test_update_status_is_case_insensitive(runner):
    _add(runner, status="applied")
    result = runner.invoke(cli, ["update", "1", "--status", "INTERVIEW"])
    assert result.exit_code == 0
    assert "interview" in result.output


def test_update_no_options_is_noop(runner):
    _add(runner, company="Corp", status="applied")
    result = runner.invoke(cli, ["update", "1"])
    assert result.exit_code == 0
    assert "Corp" in result.output
    assert "applied" in result.output


def test_update_invalid_status_prints_error(runner):
    _add(runner)
    result = runner.invoke(cli, ["update", "1", "--status", "promoted"])
    assert result.exit_code != 0
    assert "Invalid status 'promoted'" in result.output
    assert "applied" in result.output  # valid options listed


def test_update_unknown_id_prints_error(runner):
    result = runner.invoke(cli, ["update", "999", "--status", "offer"])
    assert result.exit_code != 0
    assert "No application found with ID 999" in result.output


def test_update_does_not_affect_other_rows(runner):
    _add(runner, company="Alpha", status="applied")
    _add(runner, company="Beta", status="applied")
    runner.invoke(cli, ["update", "1", "--status", "offer"])
    show = runner.invoke(cli, ["show", "2"])
    assert "applied" in show.output


# --- stubs for commands not yet implemented ---

def test_delete_confirmed(runner): ...
def test_delete_aborted(runner): ...
def test_delete_unknown_id(runner): ...
