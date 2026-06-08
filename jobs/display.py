"""Output helpers for formatting application data in the terminal."""

import sqlite3


def print_table(applications: list[sqlite3.Row]) -> None:
    """Print applications as a fixed-width table with columns: ID, Company, Role, Status, Date Applied."""
    ...


def print_detail(application: sqlite3.Row) -> None:
    """Print all fields of a single application in a labeled key-value format."""
    ...
