import pkg_resources
import click
from dateutil.tz import tzlocal
from typing import List, Optional

from mnotes.utility.file_system import FileSystem
from mnotes.notes.markdown_notes import NoteBuilder
from mnotes.notes.index import IndexBuilder, GlobalIndices
from mnotes.environment import MnoteEnvironment, load_config, load_global_index_data
import mnotes.fix
import mnotes.config


mnote_version = pkg_resources.require("m-notes")[0].version


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.core.Context):
    click.echo()
    click.echo(click.style(f"M-Notes (v{mnote_version}) Markdown Note Manager", bold=True, underline=True))

    # Load the environment configuration data and global index structure and any cached indices
    config = load_config()
    global_data = load_global_index_data()

    # This inverted dependency structure constructs the shared environment object graph. This is critical to
    # being able to separate out the different components for unit testing with a mock filesystem
    provider = FileSystem()
    note_builder = NoteBuilder(provider, tzlocal())
    index_builder = IndexBuilder(provider, note_builder)
    global_index = GlobalIndices(index_builder, directory=global_data.directory,
                                 cached=global_data.cached_indices)

    ctx.obj = MnoteEnvironment(config, global_index)
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



