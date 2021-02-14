import os
import click
from mnotes.notes.markdown_notes import NoteInfo
from typing import Optional, Tuple, List, Set, Callable


def echo_problem_title(issue: str, note: NoteInfo):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


def check_for_missing_attr(notes: List[NoteInfo], checker: Callable[[NoteInfo], bool]) -> List[NoteInfo]:
    missing = []
    for note in notes:
        if checker(note):
            missing.append(note)
    return missing
