"""
    Fix IDs Mode
"""
import click
from typing import List, Optional, Set

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

from .common import echo_problem_title, echo_color
from mnotes.notes.markdown_notes import load_all_notes, get_existing_ids, NoteMetadata
from mnotes.notes.checks import note_checks, long_stamp_format


def mode(working_path: str, files: List, count: Optional[int], resolve: bool):
    all_notes = load_all_notes(working_path)
    if not files:
        working = list(all_notes)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    try:
        all_ids = get_existing_ids(all_notes)
    except ValueError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        return

    changes = []
    new_ids: Set[str] = set()
    conflicts = 0
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["id"]["check"](note):
            echo_problem_title("Missing ID", note)

            if note.created is None:
                echo_color(" * cannot generate ID for this note, it has ", "no creation time", "red")
                continue

            new_id = note.created.strftime(long_stamp_format)
            has_conflict = False
            if new_id in all_ids:
                echo_color(f" * cannot create ID {new_id} because it ", "conflicts with an existing ID", "red",
                           " in the corpus")
                has_conflict = True

            if new_id in new_ids:
                echo_color(f" * cannot create ID {new_id} because it ", "conflicts with a proposed ID", "red")
                has_conflict = True

            if has_conflict:
                if resolve:
                    combined = all_ids.copy()
                    combined.update(new_ids)
                    new_c_time = suggest_conflict_fix(note, combined)
                    offset = abs((new_c_time - note.created).seconds)
                    new_id = new_c_time.strftime(long_stamp_format)

                    echo_color(f" * propose changing note creation time by ",
                               f"{offset} seconds to {new_c_time}", "blue")
                    echo_color(" * new ID would then be ", f"{new_id}", "blue")
                    changes.append((note, new_id, new_c_time))
                    new_ids.add(new_id)
                    continue

                else:
                    conflicts += 1
                    continue

            echo_color(" * id from creation timestamp = ", f"{new_id}", "blue")
            new_ids.add(new_id)
            changes.append((note, new_id, None))

    click.echo()
    if conflicts > 0:
        click.echo(click.style(f"There were {conflicts} conflicts. Consider running with the --resolve option.",
                               fg="red"))

    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, value, new_timestamp in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.id = value
            if new_timestamp is not None:
                note_with_content.created = new_timestamp
            note_with_content.save_file()

    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))


def suggest_conflict_fix(note: NoteMetadata, existing_ids: Set[str]) -> DateTime:
    proposed = note.created
    while proposed.strftime(long_stamp_format) in existing_ids:
        proposed = proposed + TimeDelta(seconds=1)

    return proposed


