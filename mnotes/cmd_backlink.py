import sys
import time

import click
from typing import List, Dict, Optional
from mnotes.environment import MnoteEnvironment, pass_env, echo_line
from mnotes.notes.markdown_notes import NoteInfo


@click.group(invoke_without_command=True, name="backlink")
@click.pass_context
@pass_env
def main(env: MnoteEnvironment, ctx: click.core.Context):
    """ Generate backlinks in files. """
    style = env.config.styles
    echo_line(" * backlink mode")

    # Update the global index
    start_time = time.time()
    env.global_index.load_all()
    end_time = time.time()
    echo_line(style.success(f" * updated global index, took {end_time - start_time:0.2f} seconds"))


@main.command(name="set")
@click.argument("on_off", type=click.Choice(["on", "off"], case_sensitive=False))
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def set_backlinks(env: MnoteEnvironment, on_off: click.Choice, files: List[click.Path]):
    """
    Mark the specified files (or contents of directory) to have [or not] backlinks generated for them when the
    'mnote backlink gen' command is run.

    If no specific files are specified, M-Notes will set the backlink parameter for all notes in the current
    directory and below
    """
    index = env.index_of_cwd
    style = env.config.styles

    if index is None:
        echo_line()
        echo_line(style.fail("The current working directory isn't in any of M-Notes' indices."))
        echo_line(style.warning(" * M-Notes only operates on directories it's been told to index"))
        echo_line(style.warning(" * See 'mnote index --help' for more information"))
        return

    echo_line(" * currently operating in the index: ", style.visible(index.name, underline=True))
    notes = index.notes_in_path(env.cwd)
    echo_line(" * notes or below in current directory: ", style.visible(f"{len(notes)}"))
    echo_line()

    working = index.load_working(env.cwd, files)
    if working is None:
        echo_line(style.fail("No valid notes were found to operate on in the current directory"))
        return

    mode = str(on_off).lower() == "on"
    mode_text = style.success("ON") if mode else style.fail("OFF")
    echo_line(style.visible(str(mode)))
    changes = []
    for note in working:
        if note.has_backlink == mode:
            continue
        echo_line("Set backlinks ", mode_text, " for ", style.visible(note.file_name))
        changes.append(note)

    echo_line()
    if not changes:
        echo_line(click.style(f"Checked {len(working)} notes and none needed to be changed", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note in changes:
            note_with_content = env.note_builder.load_note(note.file_path)
            note_with_content.info.backlink = mode
            with env.provider.write_file(note.file_path) as handle:
                handle.write(note_with_content.to_file_text())
    else:
        echo_line(style.fail("User rejected changes"))




