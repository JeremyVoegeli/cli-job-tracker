# CLI Job Tracker

A command-line tool for tracking job applications during a job search. Applications are stored in a local SQLite database — no account, no internet connection required. This project was made with the purpose of experimenting and getting familiar with using Claude Code in development.

## Tech Stack

- **Python 3.9+**
- **[Click](https://click.palletsprojects.com/)** — CLI framework
- **SQLite** (`sqlite3` stdlib) — local database
- **pytest** — test suite

## Installation

```bash
git clone https://github.com/your-username/cli-job-tracker.git
cd cli-job-tracker
pip install -e .
```

This registers the `jobtracker` command globally in your environment.

## Usage

### `jobtracker add`

Interactively add a new job application. Company and role are required; all other fields have defaults.

```
$ jobtracker add
Company: Anthropic
Role: Software Engineer
Date applied [2026-06-08]:
Status [applied]:
Notes: Referred by a contact
Added application #1 — Anthropic, Software Engineer (applied)
```

Valid status values: `applied`, `interview`, `offer`, `rejected`, `withdrawn`

---

### `jobtracker list`

List all applications in a table, sorted by date applied (newest first).

```
$ jobtracker list
ID  Company       Role                  Status      Date Applied
--  -----------   -------------------   ---------   ------------
4   Anthropic     Software Engineer     applied     2026-06-08
3   Acme Corp     Backend Engineer      interview   2026-06-01
2   Globex        Junior Developer      rejected    2026-05-28
1   Initech       SWE Intern            withdrawn   2026-05-20
```

Use `--status` to filter by status:

```
$ jobtracker list --status interview
ID  Company       Role                  Status      Date Applied
--  -----------   -------------------   ---------   ------------
3   Acme Corp     Backend Engineer      interview   2026-06-01
```

---

### `jobtracker show <id>`

Show full details for a single application, including notes and timestamps.

```
$ jobtracker show 3
ID:           3
Company:      Acme Corp
Role:         Backend Engineer
Status:       interview
Date Applied: 2026-06-01
Notes:        Phone screen scheduled for June 12
Created:      2026-06-01 09:15:00
Updated:      2026-06-03 14:22:00
```

---

### `jobtracker update <id>`

Update the status and/or notes on an existing application.

```
$ jobtracker update 3 --status offer --notes "Verbal offer received"
Updated application #3 — Acme Corp, Backend Engineer (offer)
```

Options:
- `--status` — new status value
- `--notes` — replace the notes field

---

### `jobtracker delete <id>`

Delete an application by ID. Prompts for confirmation before deleting.

```
$ jobtracker delete 3
Delete Acme Corp — Backend Engineer? [y/N]: y
Deleted application #3.
```

Press Enter or type `N` to cancel without deleting.

---

## Configuration

By default, the database is stored at `~/.jobs_tracker.db`. Override this by setting the `DB_PATH` environment variable:

```bash
export DB_PATH=/path/to/custom.db
```

## Running Tests

```bash
pip install pytest
pytest
```
