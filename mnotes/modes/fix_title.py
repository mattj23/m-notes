"""
    Fix missing title metadata
"""
import re
import click
from typing import List, Optional

from .common import echo_color, echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from mnotes.notes.checks import note_checks

header_pattern = re.compile("^# (.*)")


def mode(working_path: str, files: List, count: Optional[int]):
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

        if note_checks["title"]["check"](note):
            echo_problem_title("Missing Title", note)

            note_with_content = NoteMetadata(note.file_path, store_content=True)
            content = note_with_content.content.strip().split("\n")
            header = header_pattern.findall(content[0])
            if header:
                title = header[0].strip()
                echo_color(" * header found in content: ", f"{title}", "blue")
                changes.append((note, title))
            else:
                echo_color(" * ", "no header", "red", " found in content")

    click.echo()
    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, new_title in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.title = new_title
            note_with_content.save_file()
    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))

