"""
    Summary mode, which displays an overview of the corpus
"""
import os
import time
from typing import List, Optional

import click
import sys
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

from .common import CreationFixer, AuthorFixer, TitleFixer, FilenameFixer, IdFixer, Fixer
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

    order = [
        CreationFixer(env.note_builder, env.local_tz),
        IdFixer(env.note_builder, False),
        TitleFixer(env.note_builder),
        FilenameFixer(env.note_builder, False),
        AuthorFixer(env.note_builder, env.config.author)
    ]

    for check in order:
        check: Fixer
        missing = list(filter(check.check, notes))
        if missing:
            echo_line()
            echo_line(style.warning(f"Found {len(missing)} notes that are {check.description}"))
            for note in missing[:n]:
                echo_line(f" -> {note.rel_path(env.cwd)}")
            remaining = len(missing) - n
            if remaining > 0:
                echo_line(f" -> ... and {remaining} more")

            echo_line(style.visible(f" ({check.hint})"))

    end_time = time.time()
    echo_line()
    echo_line(style.success(f"Took {end_time - start_time:0.2f} seconds"))


@main.command(name="created")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@pass_env
def fix_created(env: MnoteEnvironment, files: List, n: Optional[int]):
    fixer = CreationFixer(env.note_builder, env.local_tz, env.config.styles)
    process_fixes(fixer, env, files, n)


@main.command(name="id")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--resolve", "resolve", flag_value=True,
              help="Attempt to resolve ID conflicts by adjusting creation time")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_id(env: MnoteEnvironment, files: List[click.Path], n: Optional[int], resolve: bool):
    fixer = IdFixer(env.note_builder, resolve, env.config.styles)
    process_fixes(fixer, env, files, n)


@main.command(name="filename")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@click.option("--force", "force", flag_value=True,
              help="Run the rename on all notes specified (use with --complete)")
@pass_env
def fix_filename(env: MnoteEnvironment, files: List, n: Optional[int], complete: bool, force: bool):
    fixer = FilenameFixer(env.note_builder, complete, env.config.styles)
    process_fixes(fixer, env, files, n, complete and force)


@main.command(name="author")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("-a", "--author", default=None, type=str, help="Name of author to assign (leave empty for default)")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_author(env: MnoteEnvironment, n: Optional[int], author: Optional[str], files: List):
    fixer = AuthorFixer(env.note_builder, author if author else env.config.author, env.config.styles)
    process_fixes(fixer, env, files, n)


@main.command(name="title")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_title(env: MnoteEnvironment, files: List[click.Path], n: Optional[int]):
    fixer = TitleFixer(env.note_builder, env.config.styles)
    process_fixes(fixer, env, files, n)


def process_fixes(fixer: Fixer, env: MnoteEnvironment, files: List, n: Optional[int], override_check: bool = False):
    style = env.config.styles
    # Index is guaranteed to have a value, as if it didn't we would have exited on the main command
    index = env.index_of_cwd
    working = index.load_working(env.cwd, files)
    if working is None:
        echo_line()
        echo_line(style.warning("No files to work on after checking the current directory against the index."))

    transaction = env.global_index.create_empty_transaction()
    changes = 0

    for note in working:
        if n is not None and changes >= n:
            break

        if fixer.check(note) or override_check:
            echo_line()
            desc = fixer.description[0].upper() + fixer.description[1:]
            rel_path = os.path.relpath(note.file_path, env.cwd)
            title = note.title if note.title else rel_path
            echo_line(click.style(f"{desc}: ", bold=True), click.style(f"{title}", underline=True))
            echo_line(f" * filename: {rel_path}")

            result = fixer.try_change(note.file_path, transaction)

            for line in result.message:
                echo_line(*line)

            if result.is_ok:
                transaction.add_change(note.file_path, result.change)
                changes += 1

    echo_line()
    if changes == 0:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {changes} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        env.global_index.apply_transaction(transaction)
    else:
        echo_line(style.fail("User rejected changes"))
