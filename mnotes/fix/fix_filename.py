"""
    Fix IDs Mode
"""
import os
import shutil
import re
import click
from typing import List, Optional

from .common import echo_problem_title, load_working, Fixer
from mnotes.environment import MnoteEnvironment, pass_env, echo_line, Styles
from ..notes.markdown_notes import NoteInfo, NoteBuilder
from ..utility.change import ChangeTransaction, TryChangeResult, NoteChange

date_test_pattern = re.compile(r"^20[\d\.\-\_\s]*\d")
valid_chars_pattern = re.compile(r"[^a-z0-9]")
delete_words = {"on", "to", "the", "of", "and", "is", "at", "a", "an", "for", "in"}


class FilenameFixer(Fixer):
    def __init__(self, builder: NoteBuilder, resolve: bool, style: Styles = None):
        super().__init__(builder, style)
        self.complete = resolve
        self.description = "missing an id in the filename"
        self.hint = "try the 'mnote fix title' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.id is None or note_info.id not in note_info.file_name

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []

        if note_info.id is None:
            desc.append([" * cannot add ID to filename because ", self.warn("note does not have an ID!")])
            return TryChangeResult.failed(desc)

        if self.complete and note_info.title is None:
            desc.append([" * can't do a complete rename on this note because the ", self.warn("title is empty")])
            return TryChangeResult.failed(desc)

        directory = os.path.dirname(note_info.file_path)
        proposed_filename = complete_rewrite(note_info) if self.complete else prepend_id(note_info)

        if proposed_filename == note_info.file_name:
            desc.append([self.success(" * note already has the proposed name")])
            return TryChangeResult.nothing(desc)

        proposed_path = os.path.join(directory, proposed_filename)
        proposed_rel = os.path.relpath(proposed_path, start=os.curdir)

        if proposed_path in transaction.file_paths:
            desc.append([f" * cannot rename to '{proposed_rel}' because ", self.warn("another file already exists"),
                         " at that location"])
            return TryChangeResult.failed(desc)

        desc.append([" * proposed new filename: ", self.vis(f"{proposed_rel}")])
        change = NoteChange(note_info, self, data=proposed_path)
        return TryChangeResult.ok(change, desc)

    def apply_change(self, change: NoteChange):
        self.builder.provider.move_file(change.note_info.file_path, change.change_data)


@click.command(name="filename")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@click.option("--force", "force", flag_value=True,
              help="Run the rename on all notes specified (use with --complete)")
@pass_env
def fix_filename(env: MnoteEnvironment, files: List, n: Optional[int], complete: bool, force: bool):
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
    if working is None:
        return

    style = env.config.styles

    changes = []
    proposed_paths = set()
    conflicts = 0
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["filename"]["check"](note) or (complete and force):
            echo_problem_title("Note to Change Filename", note)

            if note.id is None:
                echo_line(" * cannot add ID to filename because ", style.warning("note does not have an ID!"))
                continue

            if complete and note.title is None:
                echo_line(" * can't do a complete rename on this note because the ", style.warning("title is empty"))
                continue

            directory = os.path.dirname(note.file_path)
            proposed_filename = complete_rewrite(note) if complete else prepend_id(note)

            if proposed_filename == note.file_name:
                echo_line(style.success(" * note already has the proposed name"))
                continue

            proposed_path = os.path.join(directory, proposed_filename)
            proposed_rel = os.path.relpath(proposed_path, start=os.curdir)

            if os.path.exists(proposed_path):
                echo_line(f" * cannot rename to '{proposed_rel}' because ",
                          style.warning("another file already exists"), " at that location")
                conflicts += 1
                continue

            if proposed_path in proposed_paths:
                echo_line(f" * cannot rename to '{proposed_rel}' because ",
                          style.warning("another file with that name"), " has already been proposed")
                conflicts += 1
                continue

            echo_line(" * proposed new filename: ", style.visible(f"{proposed_rel}"))
            changes.append((note, proposed_path))

    click.echo()
    if conflicts > 0:
        echo_line(style.warning(f"There were {conflicts} conflicts"))

    if not changes:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note, value in changes:
            echo_line()
            echo_line(f"Moving {note.title}")
            echo_line(f" -> from: {os.path.relpath(note.file_path, start=os.curdir)}")
            echo_line(f" -> to:   {os.path.relpath(value, start=os.curdir)}")
            shutil.move(note.file_path, value)
    else:
        echo_line(style.fail("User rejected changes"))


def prepend_id(note: NoteInfo) -> str:
    base_name, extension = os.path.splitext(note.file_name)
    return f"{note.id}-{base_name.strip()}{extension}"


def add_words_up_to(length: int, word_set: List[str]) -> List[str]:
    working_words = list(word_set)
    built_words = []
    while working_words:
        active_word = working_words.pop(0)
        temp = built_words + [active_word]
        if len(temp) == 1 or len("-".join(temp)) < length:
            built_words = list(temp)
        else:
            return built_words
    return built_words


def complete_rewrite(note: NoteInfo) -> str:
    # Remove leading dates
    working = date_test_pattern.sub("", note.title.lower())
    working = valid_chars_pattern.sub(" ", working)
    all_words = working.split()
    cleaned_words = [word for word in all_words if word not in delete_words]

    enough_words = add_words_up_to(64, cleaned_words)
    working = "-".join(enough_words)

    return f"{note.id}-{working}.md"

