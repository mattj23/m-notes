"""
    Commands for index operations
"""
import os
import re
import sys
import time
from typing import List
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime as DateTime

import click
from mnotes.environment import MnoteEnvironment, pass_env, echo_line, save_global_index_data
from mnotes.notes.index import NoteIndex
from mnotes.notes.markdown_notes import NoteInfo

valid_chars_pattern = re.compile(r"[^a-z0-9\-]")


@click.group(name="index", invoke_without_command=True)
@click.pass_context
@pass_env
def main(env: MnoteEnvironment, ctx: click.core.Context):
    """ Manage M-Notes' global directory of indices. Indices represent folders containing indexed notes."""
    style = env.config.styles
    env.global_index.load_all()

    echo_line(" * index mode")
    if len(env.global_index.indices) == 0 and ctx.invoked_subcommand != "create":
        echo_line(" * there are ", style.warning("no indices"), " in the global directory")
        echo_line("    -> to create an index navigate to the folder containing notes you want to add")
        echo_line("    -> then use the 'mnote index create <name>' command")
        sys.exit()

    else:
        echo_line(" * there are ", style.visible(f"{len(env.global_index.indices)}"),
                  " indices in the global directory")

    if ctx.invoked_subcommand is None:
        # Update the global index
        start_time = time.time()
        env.global_index.load_all()
        end_time = time.time()
        click.echo(style.success(f" * updated all indices, took {end_time - start_time:0.2f} seconds"))

        click.echo()
        echo_line(click.style("Current Indices in Global Directory:", bold=True))
        for index in env.global_index.indices.values():
            echo_line(" * ", style.visible(index.name), f" ({len(index.notes)} notes): {index.path}")

        echo_line()
        echo_line(style.visible(" (use 'mnote index reload' to rebuild with checksums)"))


@main.command(name="zip")
@click.argument("names", type=str, nargs=-1)
@pass_env
def zip_cmd(env: MnoteEnvironment, names: List[str]):
    """
    Archive an index or multiple/all indices in zip files

    Creates archives of the markdown notes (text files only, no resources) of the indices by compressing them into zip
    files.  The files will be named with the index name and the current date and time and saved in the current
    directory. This command can be run from anywhere on the machine, it does not need to be run from inside any of the
    index folders.

    You can specify a single index by name, several indices, or leave the 'name' argument blank in order to back up
    all of them at once.
    """
    style = env.config.styles
    click.echo()

    failed = False
    for index_name in names:
        if index_name not in env.global_index.indices:
            echo_line(style.fail(f"There is no index named '{index_name}' to archive!"))
            failed = True
    if failed:
        return

    if not names:
        echo_line(style.visible("No index(s) specified, so zipping all of them..."))
        names = [i.name for i in env.global_index.indices.values()]

    start = time.time()
    for name in names:
        echo_line()
        echo_line(click.style("Zipping index ", bold=True), style.visible(f"'{name}'", bold=True))

        index: NoteIndex = env.global_index.indices[name]

        now = DateTime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_name = os.path.join(env.cwd, f"{name}-{now}.zip")
        with ZipFile(output_name, "w") as zip_handle:
            with click.progressbar(index.notes.values()) as notes:
                for note in notes:
                    note: NoteInfo
                    zip_handle.write(note.file_path,
                                     arcname=os.path.relpath(note.file_path, start=index.path),
                                     compress_type=ZIP_DEFLATED)

    end = time.time()
    echo_line()
    echo_line(style.success(f"Operation completed in {end - start:0.1f} seconds"))


@main.command(name="reload")
@pass_env
def reload(env: MnoteEnvironment):
    """
    Rebuild all indices using checksums.

    M-Notes by default will verify the integrity of its cached data by looking at the file size and last modified
    timestamp to guess at whether the file has changed since it was last read (this is similar to the method which
    rsync uses) However, it's up to the file system to report these values accurately, so this option uses the SHA1
    checksum to rebuild the indicies. It's faster than re-reading all of the files, but slower than simply looking at
    the file size and timestamps.
    """
    style = env.config.styles

    start_time = time.time()
    env.global_index.load_all(True)
    end_time = time.time()
    click.echo(style.success(f"Updated all indices with checksums, took {end_time - start_time:0.2f} seconds"))


@main.command(name="delete")
@click.argument("name", type=str)
@pass_env
def delete(env: MnoteEnvironment, name: str):
    """ Delete an index from the global directory. """
    style = env.config.styles
    click.echo()

    if name not in env.global_index.indices:
        echo_line(style.fail(f"There is no index named '{name}' to remove!"))
        return

    # If we got to this point we can create the index!
    click.echo()
    echo_line(style.warning(f"You are about to remove the index named '{name}'", bold=True))
    echo_line(style.warning(f"which maps to the folder '{env.cwd}'", bold=True))
    click.echo()
    if click.confirm(click.style(f"Apply this change?", bold=True)):
        click.echo(style.success("User deleted index"))
        del env.global_index.index_directory[name]
        save_global_index_data(env.global_index)
    else:
        click.echo(style.fail("User rejected index creation"))


@main.command(name="create")
@click.argument("name", type=str)
@pass_env
def create(env: MnoteEnvironment, name: str):
    """ Create a new index in the global directory with the specified name. """
    style = env.config.styles
    click.echo()

    # Check if this folder is already part of another index
    if env.index_of_cwd is not None:
        echo_line(style.fail(f"The current working directory is already part of an index named "
                             f"'{env.index_of_cwd.name}'. Indexes cannot be contained by other indexes"))
        return

    # Check if this index would contain another index
    contained = env.indices_in_cwd
    if contained:
        echo_line(style.fail("The following already-existing indices are subdirectories of the current working "
                             "directory. You can't create an index here because indexes cannot be contained by other "
                             "indexes."))
        for index in contained:
            echo_line(f" * {index.name}: {index.path}")
        return

    # Check if the name given is valid
    if valid_chars_pattern.findall(name):
        echo_line("The name ", style.fail(f"'{name}'"), " contains invalid characters for an index name")
        click.echo()
        echo_line("Index names may contain numbers, lowercase letters, and dashes only. Also consider that shorter "
                  "names are faster to type.  Think of the index name as a nickname or an alias for the folder you"
                  "are adding to the global directory.")
        return

    if name in env.global_index.indices:
        echo_line("The name ", style.fail(f"'{name}'"), " is already used by another index.")
        click.echo()
        echo_line("Index names may contain numbers, lowercase letters, and dashes only. Also consider that shorter "
                  "names are faster to type.  Think of the index name as a nickname or an alias for the folder you"
                  "are adding to the global directory.")

    # Check for conflicts before allowing M-Notes to add this as an index
    conflicts = env.global_index.find_conflicts(env.cwd)
    if conflicts:
        echo_line(style.fail("There are ID conflicts which would be created if this folder is merged into the global"
                             "directory as it is."))
        for id_, conflict in conflicts.items():
            click.echo()
            echo_line(style.warning(f"Conflict for ID {id_}:", bold=True))
            for e in conflict.existing:
                echo_line(style.visible(f" * Already in global: {e.file_path}"))

            for c in conflict.conflicting:
                echo_line(style.warning(f" * In this directory: {c.file_path}"))

        return

    # If we got to this point we can create the index!
    click.echo()
    echo_line(style.warning(f"You are about to create an index named '{name}'", bold=True))
    echo_line(style.warning(f"which will be located in the folder '{env.cwd}'", bold=True))
    click.echo()
    if click.confirm(click.style(f"Apply this change?", bold=True)):
        click.echo(style.success("User created index"))
        env.global_index.index_directory[name] = {"path": env.cwd}
        save_global_index_data(env.global_index)
    else:
        click.echo(style.fail("User rejected index creation"))
