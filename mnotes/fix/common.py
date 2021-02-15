import os
import click
from mnotes.notes.markdown_notes import NoteInfo
from mnotes.notes.index import NoteIndex
from typing import Optional, Tuple, List, Set, Callable


def echo_problem_title(issue: str, note: NoteInfo):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


def load_working(index: NoteIndex, path: str, files: List) -> List[NoteInfo]:
    if not files:
        return index.notes_in_path(path)
    else:
        abs_paths = map(os.path.abspath, files)
        return [index.notes[f] for f in abs_paths if f in index.notes]

