"""
    Fix IDs Mode
"""
import os
import shutil
import re
import click
from typing import List, Optional

from .common import echo_color, echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from mnotes.notes.checks import note_checks


date_test_pattern = re.compile(r"^20[\d\.\-\_\s]*\d")
valid_chars_pattern = re.compile(r"[^a-z0-9]")
delete_words = {"on", "to", "the", "of", "and", "is", "at", "a", "an", "for", "in"}


def prepend_id(note: NoteMetadata) -> str:
    base_name, extension = os.path.splitext(note.file_name)
    return f"{note.id}_{base_name.strip()}{extension}"


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


def complete_rewrite(note: NoteMetadata) -> str:
    # Remove leading dates
    working = date_test_pattern.sub("", note.title.lower())
    working = valid_chars_pattern.sub(" ", working)
    all_words = working.split()
    cleaned_words = [word for word in all_words if word not in delete_words]

    enough_words = add_words_up_to(64, cleaned_words)
    working = "-".join(enough_words)

    return f"{note.id}-{working}.md"


def mode(working_path: str, files: List, count: Optional[int], complete: bool, force: bool):
    if not files:
        working = load_all_notes(working_path)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    changes = []
    proposed_paths = set()
    conflicts = 0
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["filename"]["check"](note) or (complete and force):
            echo_problem_title("Note to Change Filename", note)

            if note.id is None:
                echo_color(" * cannot add ID to filename because ", "note does not have an ID!", "red")
                continue

            if complete and note.title is None:
                echo_color(" * can't do a complete rename on this note because the ", "title is empty", "red")
                continue

            directory = os.path.dirname(note.file_path)
            proposed_filename = complete_rewrite(note) if complete else prepend_id(note)

            if proposed_filename == note.file_name:
                print(" * note already has the proposed name")
                continue

            proposed_path = os.path.join(directory, proposed_filename)
            proposed_rel = os.path.relpath(proposed_path, start=os.curdir)

            if os.path.exists(proposed_path):
                echo_color(f" * cannot rename to '{proposed_rel}' because ", "another file already exists", "red",
                           " at that location")
                conflicts += 1
                continue

            if proposed_path in proposed_paths:
                echo_color(f" * cannot rename to '{proposed_rel}' because ", "another file with that name", "red",
                           " has already been proposed")
                conflicts += 1
                continue

            echo_color(" * proposed new filename: ", f"{proposed_rel}", "blue")
            changes.append((note, proposed_path))

    click.echo()
    if conflicts > 0:
        click.echo(click.style(f"There were {conflicts} conflicts", fg="red"))

    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, value in changes:
            print(f"\nMoving {note.title}")
            print(f" -> from: {os.path.relpath(note.file_path, start=os.curdir)}")
            print(f" -> to:   {os.path.relpath(value, start=os.curdir)}")
            shutil.move(note.file_path, value)
    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))



