"""
    Fix missing creation timestamps
"""
import click
from typing import List, Optional

from .common import echo_problem_title
from mnotes.notes.markdown_notes import NoteMetadata, local_time_zone, load_all_notes
from mnotes.notes.checks import note_checks, long_stamp_pattern, from_timestamp_id, file_c_time
from mnotes.environment import MnoteEnvironment, pass_env, echo_line


@click.command(name="created")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@pass_env
def fix_created(env: MnoteEnvironment, files: List, n: Optional[int]):
    if not files:
        working = load_all_notes(env.cwd)
    else:
        working = [NoteMetadata(f) for f in files]
    if working is None:
        return

    style = env.config.styles

    changes = []
    for note in working:
        if n is not None and len(changes) >= n:
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
                    echo_line(" * file had long-stamp but it ",  style.warning("didn't parse to a valid date/time"))
                    continue

            if got_long_stamp:
                time_stamp = local_time_zone.localize(converted)
                echo_line(" * found timestamp in file name: ", style.visible(f"{time_stamp}"))
                changes.append((note, time_stamp))

            else:
                c_time, is_created = file_c_time(note.file_path)
                c_time = local_time_zone.localize(c_time)
                extract_mode = 'created' if is_created else 'last modified'
                echo_line(f" * extracted ", style.visible(extract_mode), " timestamp from file system: ",
                          style.visible(f"{c_time}"))
                changes.append((note, c_time))

    if not changes:
        click.echo()
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    click.echo()
    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(style.success("User accepted changes"))
        for note, value in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.created = value
            note_with_content.save_file()
    else:
        click.echo(style.fail("User rejected changes"))


