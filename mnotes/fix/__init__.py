"""
    Summary mode, which displays an overview of the corpus
"""
import os
import time
from typing import List, Optional, Callable

import click
import sys
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

from .common import CreationFixer, AuthorFixer, TitleFixer, FilenameFixer, IdFixer, Fixer
from ..notes.markdown_notes import NoteInfo
from ..utility.change import ChangeTransaction


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
    echo_line(style.success(f" * updated global directory, took {end_time - start_time:0.2f} seconds"))

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
    process_fixes(single_core(fixer, n, False, env), env, files)


@main.command(name="id")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--resolve", "resolve", flag_value=True,
              help="Attempt to resolve ID conflicts by adjusting creation time")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_id(env: MnoteEnvironment, files: List[click.Path], n: Optional[int], resolve: bool):
    fixer = IdFixer(env.note_builder, resolve, env.config.styles)
    process_fixes(single_core(fixer, n, False, env), env, files)


@main.command(name="filename")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@click.option("--force", "force", flag_value=True,
              help="Run the rename on all notes specified (use with --complete)")
@pass_env
def fix_filename(env: MnoteEnvironment, files: List, n: Optional[int], complete: bool, force: bool):
    complete = complete or env.config.filename_complete
    fixer = FilenameFixer(env.note_builder, complete, env.config.styles)
    process_fixes(single_core(fixer, n, complete and force, env), env, files)


@main.command(name="author")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("-a", "--author", default=None, type=str, help="Name of author to assign (leave empty for default)")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_author(env: MnoteEnvironment, n: Optional[int], author: Optional[str], files: List):
    fixer = AuthorFixer(env.note_builder, author if author else env.config.author, env.config.styles)
    process_fixes(single_core(fixer, n, False, env), env, files)


@main.command(name="title")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_title(env: MnoteEnvironment, files: List[click.Path], n: Optional[int]):
    fixer = TitleFixer(env.note_builder, env.config.styles)
    process_fixes(single_core(fixer, n, False, env), env, files)


@main.command(name="all")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@pass_env
def fix_all(env: MnoteEnvironment, files: List, n: Optional[int], complete: bool):
    """ Equivalent to fixing created, id, title, filename, author in sequence.

    This is a highly automated command that performs a sequence of fixes. It's not safe to run on large batches of
    notes at a time so it will only allow up to 5 notes to be run at once.

    The --complete flag will rewrite the filename the same as running `mnote fix filename --complete`
    """
    complete = complete or env.config.filename_complete
    style = env.config.styles

    if n is None or n > 5:
        echo_line()
        echo_line(style.warning("This command is limited to processing five notes at a time."))
        n = 5

    def core(working: List[NoteInfo], transaction: ChangeTransaction) -> int:
        pipeline = [
            CreationFixer(env.note_builder, env.local_tz, env.config.styles),
            IdFixer(env.note_builder, True, env.config.styles),
            AuthorFixer(env.note_builder, env.config.author, env.config.styles),
            TitleFixer(env.note_builder, env.config.styles),
            FilenameFixer(env.note_builder, complete, env.config.styles)
        ]

        changes = 0
        for note in working:
            if changes >= n:
                break

            has_change = False

            for fixer in pipeline:
                if fixer.check(note):
                    if not has_change:
                        # This should be the first printing of the note. It's structured like this so that the
                        # note will never be printed unless it has something wrong with it any stage of the
                        # pipeline
                        rel_path = os.path.relpath(note.file_path, env.cwd)
                        title = note.title if note.title else rel_path
                        echo_line()
                        echo_line(click.style("Fix All For: ", bold=True), click.style(f"{title}", underline=True))
                        echo_line(f" * filename: {rel_path}")
                        has_change = True

                    result = fixer.try_change(note.file_path, transaction)

                    echo_line(" * note is ", style.warning(fixer.description))
                    for line in result.message:
                        echo_line(*line)

                    if result.is_ok:
                        transaction.add_change(note.file_path, result.change)

            if has_change:
                changes += 1
        return changes

    process_fixes(core, env, files)


def single_core(fixer: Fixer, n: Optional[int], override_check: bool, env: MnoteEnvironment) -> Callable[
    [List[NoteInfo], ChangeTransaction], int]:
    """ Returns a curried function that performs a single fixer run for the central core to the process_fixes
    function. """

    def curried(working: List[NoteInfo], transaction: ChangeTransaction) -> int:
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
        return changes

    return curried


def process_fixes(core: Callable[[List[NoteInfo], ChangeTransaction], int], env: MnoteEnvironment, files: List):
    style = env.config.styles
    # Index is guaranteed to have a value, as if it didn't we would have exited on the main command
    index = env.index_of_cwd
    working = index.load_working(env.cwd, files)
    if working is None:
        echo_line()
        echo_line(style.warning("No files to work on after checking the current directory against the index."))

    transaction = env.global_index.create_empty_transaction()
    changes = core(working, transaction)

    echo_line()
    if changes == 0:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {changes} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        env.global_index.apply_transaction(transaction)
    else:
        echo_line(style.fail("User rejected changes"))
