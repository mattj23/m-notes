"""
    Summary mode, which displays an overview of the corpus
"""

import time
import click
from mnotes.fix.common import check_for_missing_attr
from mnotes.notes.markdown_notes import load_all_notes
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env

from .fix_created import fix_created
from .fix_author import fix_author
from .fix_title import fix_title
from .fix_filename import fix_filename
from .fix_ids import fix_id


@click.group(name="fix", invoke_without_command=True)
@click.option("-n", default=5, show_default=True)
@click.pass_context
@pass_env
def mode(env: MnoteEnvironment, ctx: click.core.Context, n: int):
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
            click.echo(click.style(f"Found {len(missing)} notes that are {check['description']}", fg="red"))
            for note in missing[:n]:
                click.echo(click.style(f" -> {note.rel_path(env.cwd)}"))
            remaining = len(missing) - n
            if remaining > 0:
                click.echo(click.style(f" -> ... and {remaining} more"))

            click.echo(click.style(f" ({check['hint']})"))

    end_time = time.time()
    print(f"\nTook {end_time - start_time:0.2f} seconds")


mode.add_command(fix_created)
mode.add_command(fix_author)
mode.add_command(fix_title)
mode.add_command(fix_filename)
mode.add_command(fix_id)
