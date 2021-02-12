"""
    Fix missing title metadata
"""
import re
import click
from typing import List, Optional

from .common import echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

header_pattern = re.compile("^# (.*)")


@click.command(name="title")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_title(env: MnoteEnvironment, files: List[click.Path], n: Optional[int]):
    if not files:
        working = load_all_notes(env.cwd)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    style = env.config.styles

    changes = []
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["title"]["check"](note):
            echo_problem_title("Missing Title", note)

            note_with_content = NoteMetadata(note.file_path, store_content=True)
            content = note_with_content.content.strip().split("\n")
            header = header_pattern.findall(content[0])
            if header:
                title = header[0].strip()
                echo_line(" * header found in content", style.visible(f"{title}"))
                changes.append((note, title))
            else:
                echo_line(" * ", style.warning("no header"), " found in context")

    click.echo()
    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(style.success("User accepted changes"))
        for note, new_title in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.title = new_title
            note_with_content.save_file()
    else:
        click.echo(style.fail("User rejected changes"))

