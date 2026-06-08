"""Output helpers for formatting application data in the terminal."""

import sqlite3

import click

_LIST_HEADERS = ["ID", "Company", "Role", "Status", "Date Applied"]
_LIST_KEYS = ["id", "company", "role", "status", "date_applied"]


def print_table(applications: list[sqlite3.Row]) -> None:
    """Print applications as a fixed-width table with columns: ID, Company, Role, Status, Date Applied."""
    widths = [len(h) for h in _LIST_HEADERS]
    for row in applications:
        for i, key in enumerate(_LIST_KEYS):
            widths[i] = max(widths[i], len(str(row[key] or "")))

    gap = "  "
    click.echo(gap.join(h.ljust(w) for h, w in zip(_LIST_HEADERS, widths)).rstrip())
    click.echo(gap.join("-" * w for w in widths).rstrip())
    for row in applications:
        values = [str(row[k] or "") for k in _LIST_KEYS]
        click.echo(gap.join(v.ljust(w) for v, w in zip(values, widths)).rstrip())


def print_detail(application: sqlite3.Row) -> None:
    """Print all fields of a single application in a labeled key-value format."""
    fields = [
        ("ID",           str(application["id"])),
        ("Company",      application["company"]),
        ("Role",         application["role"]),
        ("Status",       application["status"]),
        ("Date Applied", application["date_applied"]),
        ("Notes",        application["notes"] or ""),
        ("Created",      application["created_at"]),
        ("Updated",      application["updated_at"]),
    ]
    col = max(len(label) for label, _ in fields) + 2  # +2 for ": " minimum
    for label, value in fields:
        click.echo(f"{label + ':':<{col}}{value}")
