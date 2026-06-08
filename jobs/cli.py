"""Click command definitions for the jobs CLI."""

import sys
from datetime import date

import click

from jobs import db, display


@click.group()
def cli() -> None:
    """Track job applications from the command line."""
    db.init_db()


@cli.command()
def add() -> None:
    """Prompt for application details and insert a new record."""
    company = click.prompt("Company")
    role = click.prompt("Role")
    date_applied = click.prompt("Date applied", default=date.today().isoformat())
    status = click.prompt("Status", default="applied").strip().lower()
    if status not in db.VALID_STATUSES:
        valid = ", ".join(sorted(db.VALID_STATUSES))
        click.echo(f"Invalid status '{status}'. Valid options: {valid}")
        sys.exit(1)
    notes = click.prompt("Notes", default="", show_default=False)
    row = db.add_application(company, role, date_applied, status, notes)
    click.echo(f"Added application #{row['id']} — {row['company']}, {row['role']} ({row['status']})")


@cli.command(name="list")
@click.option("--status", default=None, help="Filter by status.")
def list_cmd(status: str | None) -> None:
    """List all applications, newest first. Optionally filter by --status."""
    rows = db.list_applications(status=status.lower() if status else None)
    if not rows:
        click.echo("No applications found.")
        return
    display.print_table(rows)


@cli.command()
@click.argument("id", type=int)
def show(id: int) -> None:
    """Show full details for a single application."""
    row = db.get_application(id)
    if row is None:
        click.echo(f"No application found with ID {id}.")
        sys.exit(1)
    display.print_detail(row)


@cli.command()
@click.argument("id", type=int)
@click.option("--status", default=None, help="New status value.")
@click.option("--notes", default=None, help="Replace notes content.")
def update(id: int, status: str | None, notes: str | None) -> None:
    """Update the status and/or notes on an existing application."""
    ...


@cli.command()
@click.argument("id", type=int)
def delete(id: int) -> None:
    """Delete an application by ID after prompting for confirmation."""
    ...
