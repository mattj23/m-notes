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
def main(ctx: click.core.Context):
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


@click.command()
@click.argument("set-name", type=str)
@click.pass_context
def mgo(ctx: click.core.Context, set_name: str):
    """ Hi there! This will hopefully become a tool to help navigate between collections"""
    click.echo(f"{set_name}")


main.add_command(mnotes.config.config)
main.add_command(mnotes.fix.mode)



