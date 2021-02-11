"""
    Fix missing creation timestamps
"""
import click
from typing import List, Optional

from .common import echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, local_time_zone, load_all_notes
from mnotes.notes.checks import note_checks, long_stamp_pattern, from_timestamp_id, file_c_time


def mode(working_path: str, files: List, count: Optional[int]):
    if not files:
        working = load_all_notes(working_path)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    changes = []
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["created"]["check"](note):
            echo_problem_title("Missing Creation Time", note)

            long_stamp = long_stamp_pattern.findall(note.file_name)
            got_long_stamp = False
            converted = None
            if long_stamp:
                try:
                    converted = from_timestamp_id(long_stamp[0])
                    got_long_stamp = True
                except ValueError:
                    click.echo(click.style(f" * file had long-stamp but it didn't parse to a valid date/time", fg="red"))
                    continue

            if got_long_stamp:
                time_stamp = local_time_zone.localize(converted)
                click.echo(" * found timestamp in file name: ", nl=False)
                click.echo(click.style(f"{time_stamp}", fg="blue"))
                changes.append((note, time_stamp))

            else:
                c_time, is_created = file_c_time(note.file_path)
                c_time = local_time_zone.localize(c_time)
                extract_mode = 'created' if is_created else 'last modified'
                click.echo(f" * extracted {extract_mode} timestamp from file system: ", nl=False)
                click.echo(click.style(f"{c_time}", fg="blue"))
                changes.append((note, c_time))

    if not changes:
        click.echo()
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    click.echo()
    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(click.style("User accepted changes", fg="green", bold=True))
        for note, value in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.created = value
            note_with_content.save_file()
    else:
        click.echo(click.style("User rejected changes", fg="red", bold=True))


