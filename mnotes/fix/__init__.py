"""
    Summary mode, which displays an overview of the corpus
"""

import time
import click
import sys
from mnotes.fix.common import check_for_missing_attr
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

# from .fix_created import fix_created
# from .fix_author import fix_author
# from .fix_title import fix_title
# from .fix_filename import fix_filename
# from .fix_ids import fix_id


@click.group(name="fix", invoke_without_command=True)
@click.option("-n", default=5, show_default=True)
@click.pass_context
@pass_env
def mode(env: MnoteEnvironment, ctx: click.core.Context, n: int):
    style = env.config.styles

    index = env.index_of_cwd

    if index is None:
        echo_line(style.fail("The current working directory isn't in any of M-Notes' indices."))
        echo_line(style.warning(" * M-Notes only operates on directories it's been told to index"))
        echo_line(style.warning(" * See 'mnote index --help' for more information"))
        sys.exit()

    # Update the global index
    start_time = time.time()
    env.global_index.load_all()
    end_time = time.time()
    click.echo(style.success(f"Updated global index, took {end_time - start_time:0.4f} seconds"))

    if ctx.invoked_subcommand is not None:
        return

    start_time = time.time()

    notes = load_all_notes(env.cwd)
    click.echo(click.style(f" * notes in current directory: {len(notes)}"))

    order = ["created", "id", "title", "filename", "author"]


    for check in [note_checks[o] for o in order]:
        missing = check_for_missing_attr(notes, check["check"])
        if missing:
            click.echo()
            click.echo(style.warning(f"Found {len(missing)} notes that are {check['description']}"))
            for note in missing[:n]:
                click.echo(click.style(f" -> {note.rel_path(env.cwd)}"))
            remaining = len(missing) - n
            if remaining > 0:
                click.echo(click.style(f" -> ... and {remaining} more"))

            click.echo(style.visible(f" ({check['hint']})"))

    end_time = time.time()
    click.echo()
    click.echo(style.success(f"Took {end_time - start_time:0.2f} seconds"))


# mode.add_command(fix_created)
# mode.add_command(fix_author)
# mode.add_command(fix_title)
# mode.add_command(fix_filename)
# mode.add_command(fix_id)
