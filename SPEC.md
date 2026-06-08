# CLI Job Application Tracker — Spec

## Overview

A command-line tool for tracking job applications during a job search.
Built with Python, Click, and SQLite (stdlib). No external database required.

---

## Tech Stack

- **Language**: Python 3.10+
- **CLI framework**: Click
- **Database**: SQLite via `sqlite3` (stdlib)
- **Testing**: pytest
- **Packaging**: `pyproject.toml` with `pip install -e .`

---

## Database Schema

Single table: `applications`

| Column       | Type    | Notes                                              |
|--------------|---------|----------------------------------------------------|
| `id`         | INTEGER | Primary key, autoincrement                         |
| `company`    | TEXT    | Required                                           |
| `role`       | TEXT    | Required                                           |
| `date_applied` | TEXT  | ISO format (YYYY-MM-DD), defaults to today         |
| `status`     | TEXT    | One of: applied, interview, offer, rejected, withdrawn |
| `notes`      | TEXT    | Optional freeform text                             |
| `created_at` | TEXT    | ISO datetime, set on insert                        |
| `updated_at` | TEXT    | ISO datetime, updated on every change              |

Valid status values (enforced at CLI level):
- `applied` (default)
- `interview`
- `offer`
- `rejected`
- `withdrawn`

---

## Commands

### `jobs add`
Add a new job application.

**Prompts for:**
- Company name (required)
- Role/title (required)
- Date applied (optional, defaults to today)
- Status (optional, defaults to `applied`)
- Notes (optional)

**Example:**
```
$ jobs add
Company: Anthropic
Role: Software Engineer
Date applied [2026-06-08]:
Status [applied]:
Notes: Referred by a contact
Added application #4 — Anthropic, Software Engineer (applied)
```

---

### `jobs list`
List all applications in a table, sorted by date applied (newest first).

**Options:**
- `--status` — filter by status (e.g. `jobs list --status interview`)

**Output columns:** ID, Company, Role, Status, Date Applied

**Example:**
```
$ jobs list
ID  Company       Role                  Status      Date Applied
--  -----------   -------------------   ---------   ------------
4   Anthropic     Software Engineer     applied     2026-06-08
3   Acme Corp     Backend Engineer      interview   2026-06-01
2   Globex        Junior Developer      rejected    2026-05-28
1   Initech       SWE Intern            withdrawn   2026-05-20

$ jobs list --status interview
ID  Company       Role                  Status      Date Applied
--  -----------   -------------------   ---------   ------------
3   Acme Corp     Backend Engineer      interview   2026-06-01
```

---

### `jobs show <id>`
Show full details for a single application, including notes.

**Example:**
```
$ jobs show 4
ID:           4
Company:      Anthropic
Role:         Software Engineer
Status:       applied
Date Applied: 2026-06-08
Notes:        Referred by a contact
Created:      2026-06-08 10:32:00
Updated:      2026-06-08 10:32:00
```

---

### `jobs update <id>`
Update the status and/or notes on an existing application.

**Options:**
- `--status` — new status value
- `--notes` — replace notes content

**Example:**
```
$ jobs update 4 --status interview --notes "Phone screen scheduled for June 12"
Updated application #4 — Anthropic, Software Engineer (interview)
```

---

### `jobs delete <id>`
Delete an application by ID. Prompts for confirmation.

**Example:**
```
$ jobs delete 4
Delete Anthropic — Software Engineer? [y/N]: y
Deleted application #4.
```

---

## Project Structure

```
cli-job-tracker/
├── pyproject.toml
├── README.md
├── SPEC.md
├── jobs/
│   ├── __init__.py
│   ├── cli.py          # Click command definitions
│   ├── db.py           # All SQLite interactions
│   └── display.py      # Table formatting / output helpers
└── tests/
    ├── __init__.py
    ├── test_db.py       # Unit tests for db.py functions
    └── test_cli.py      # CLI integration tests via Click's test runner
```

---

## Behavior Notes

- Database file stored at `~/.jobs_tracker.db` by default
- `DB_PATH` environment variable overrides the default path (used in tests)
- All dates stored as ISO strings; displayed as-is
- Status values are case-insensitive on input, stored lowercase
- If an invalid status is provided, print an error and list valid options
- `jobs list` with no results prints: "No applications found."
- `jobs show` / `jobs update` / `jobs delete` with an unknown ID prints: "No application found with ID <n>."

---

## Out of Scope (for now)

- Export to CSV
- Search by company name or role
- Reminders or follow-up dates
- Color-coded terminal output