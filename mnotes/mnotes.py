import os
import pkg_resources
import click
from typing import List, Optional

from mnotes.environment import MnoteEnvironment, pass_env
import mnotes.fix
import mnotes.config


mnote_version = pkg_resources.require("m-notes")[0].version


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    click.echo()
    click.echo(click.style(f"M-Notes (v{mnote_version}) Markdown Note Manager", bold=True, underline=True))

    # Load the environment
    ctx.obj = MnoteEnvironment()
    ctx.obj.print()

    if ctx.invoked_subcommand is None:
        pass
    else:
        pass
        # running the subcommand


main.add_command(mnotes.config.config)
main.add_command(mnotes.fix.mode)



