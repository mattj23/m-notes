"""
    Fix missing title metadata
"""
import os

import click
from typing import List, Optional

from .common import echo_problem_title
from mnotes.environment import MnoteEnvironment, pass_env, echo_line


@click.command(name="author")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("-a", "--author", default=None, type=str, help="Name of author to assign (leave empty for default)")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_author(env: MnoteEnvironment, n: Optional[int], author: Optional[str], files: List):
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
    if working is None:
        return

    author = env.config.author if author is None else author
    style = env.config.styles

    changes = []
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["author"]["check"](note):
            echo_problem_title("Missing Author", note)
            echo_line(" * will set author to ", style.visible(f"'{author}'"))
            changes.append((note, author))

    echo_line()
    if not changes:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note, author in changes:
            note_with_content = env.note_builder.load_note(note.file_path)
            note_with_content.info.author = author
            with env.provider.write_file(note.file_path) as handle:
                handle.write(note_with_content.to_file_text())
    else:
        echo_line(style.fail("User rejected changes"))


