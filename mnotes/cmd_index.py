"""
    Commands for index operations
"""
import re
import sys
import time

import click
from mnotes.environment import MnoteEnvironment, pass_env, echo_line, save_global_index_data

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
