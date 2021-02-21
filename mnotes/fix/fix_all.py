"""
    Fix missing creation timestamps
"""
import click
from typing import List, Optional
from datetime import datetime as DateTime

from .common import echo_problem_title, load_working
from mnotes.notes.checks import note_checks, long_stamp_pattern, file_c_time
from mnotes.notes.markdown_notes import ID_TIME_FORMAT
from mnotes.environment import MnoteEnvironment, pass_env, echo_line


@click.command(name="all")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@pass_env
def fix_all(env: MnoteEnvironment, files: List, n: Optional[int]):
    """ Equivalent to fixing created, id, title, filename, author in sequence.

    This is a highly automated command that performs a sequence of fixes. It's not safe to run on large batches of
    notes at a time so it will only allow up to 5 notes to be run at once.

    The --complete flag will rewrite the filename the same as running `mnote fix filename --complete`
    """
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
    if working is None:
        return

    style = env.config.styles

    if n is None or n > 5:
        echo_line(style.warning("This command is limited to processing five notes at a time."))



