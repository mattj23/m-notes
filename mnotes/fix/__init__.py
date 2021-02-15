"""
    Summary mode, which displays an overview of the corpus
"""

import time
import click
import sys
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

from .fix_created import fix_created
from .fix_author import fix_author
from .fix_title import fix_title
from .fix_filename import fix_filename
from .fix_ids import fix_id


@click.group(name="fix", invoke_without_command=True)
@click.option("-n", default=5, show_default=True)
@click.pass_context
@pass_env
def main(env: MnoteEnvironment, ctx: click.core.Context, n: int):
    style = env.config.styles

    # Update the global index
    start_time = time.time()
    env.global_index.load_all()
    end_time = time.time()
    echo_line(style.success(f" * updated global index, took {end_time - start_time:0.2f} seconds"))

    # Find the current index
    index = env.index_of_cwd

    if index is None:
        echo_line(style.fail("The current working directory isn't in any of M-Notes' indices."))
        echo_line(style.warning(" * M-Notes only operates on directories it's been told to index"))
        echo_line(style.warning(" * See 'mnote index --help' for more information"))
        sys.exit()

    if ctx.invoked_subcommand is not None:
        return

    start_time = time.time()
    echo_line(" * currently operating in the index: ", style.visible(index.name, underline=True))
    notes = index.notes_in_path(env.cwd)
    echo_line(" * notes or below in current directory: ", style.visible(f"{len(notes)}"))

    order = ["created", "id", "title", "filename", "author"]

    for check in [note_checks[o] for o in order]:
        missing = list(filter(check["check"], notes))
        if missing:
            echo_line()
            echo_line(style.warning(f"Found {len(missing)} notes that are {check['description']}"))
            for note in missing[:n]:
                echo_line(f" -> {note.rel_path(env.cwd)}")
            remaining = len(missing) - n
            if remaining > 0:
                echo_line(f" -> ... and {remaining} more")

            echo_line(style.visible(f" ({check['hint']})"))

    end_time = time.time()
    echo_line()
    echo_line(style.success(f"Took {end_time - start_time:0.2f} seconds"))


main.add_command(fix_created)
main.add_command(fix_author)
main.add_command(fix_title)
main.add_command(fix_filename)
main.add_command(fix_id)
