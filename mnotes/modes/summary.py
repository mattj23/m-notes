"""
    Summary mode, which displays an overview of the corpus
"""
import time
import os
import click
from mnotes.modes.common import check_for_missing_attr
from mnotes.notes.markdown_notes import load_all_notes
from mnotes.notes.checks import note_checks


def mode(working_path: str, summary_count: int):
    start_time = time.time()

    notes = load_all_notes(working_path)
    click.echo(click.style(f" * notes in current directory: {len(notes)}"))

    order = ["created", "id", "title", "filename", "author"]

    for check in [note_checks[o] for o in order]:
        missing = check_for_missing_attr(notes, check["check"])
        if missing:
            click.echo()
            click.echo(click.style(f"Found {len(missing)} notes that are {check['description']}", fg="red"))
            for n in missing[:summary_count]:
                click.echo(click.style(f" -> {n.rel_path(working_path)}"))
            remaining = len(missing) - summary_count
            if remaining > 0:
                click.echo(click.style(f" -> ... and {remaining} more"))

            click.echo(click.style(f" ({check['hint']})"))

    end_time = time.time()
    print(f"\nTook {end_time - start_time:0.2f} seconds")
