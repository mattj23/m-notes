"""
    Fix missing title metadata
"""
import click
from typing import List, Optional

from .common import echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env


@click.command(name="author")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("-a", "--author", default=None, type=str, help="Name of author to assign (leave empty for default)")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_author(env: MnoteEnvironment, n: Optional[int], author: Optional[str], files: List):
    if not files:
        working = load_all_notes(env.cwd)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    author = env.config.author if author is None else author

    changes = []
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["author"]["check"](note):
            echo_problem_title("Missing Author", note)
            click.echo(" * will set author to ", nl=False)
            click.echo(click.style(f"'{author}'", fg="blue"))
            changes.append((note, author))

    click.echo()
    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, new_title in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.author = new_title
            note_with_content.save_file()
    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))


