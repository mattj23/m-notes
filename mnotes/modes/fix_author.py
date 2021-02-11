"""
    Fix missing title metadata
"""
import click
from typing import List, Optional

from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from mnotes.notes.checks import note_checks, long_stamp_pattern, from_timestamp_id, file_c_time


def mode(working_path: str, author: Optional[str], files: List, count: Optional[int]):
    if not files:
        working = load_all_notes(working_path)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    changes = []
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["author"]["check"](note):
            click.echo()
            click.echo(click.style(f"Missing Author: {note.title}", fg="red"))
            click.echo(f" * filename = {note.file_name}")
            click.echo(f" * will set author to '{author}'")
            changes.append((note, author))

    if not changes:
        click.echo()
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    click.echo()
    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, new_title in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.author = new_title
            note_with_content.save_file()
    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))


