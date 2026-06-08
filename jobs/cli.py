"""Click command definitions for the jobs CLI."""

import click

from jobs import db, display


@click.group()
def cli() -> None:
    """Track job applications from the command line."""
    ...


@cli.command()
def add() -> None:
    """Prompt for application details and insert a new record."""
    ...


@cli.command(name="list")
@click.option("--status", default=None, help="Filter by status.")
def list_cmd(status: str | None) -> None:
    """List all applications, newest first. Optionally filter by --status."""
    ...


@cli.command()
@click.argument("id", type=int)
def show(id: int) -> None:
    """Show full details for a single application."""
    ...


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
