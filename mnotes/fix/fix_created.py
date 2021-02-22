"""
    Fix missing creation timestamps
"""
import click
from typing import List, Optional
from datetime import datetime as DateTime

from .common import echo_problem_title
from mnotes.notes.markdown_notes import ID_TIME_FORMAT
from mnotes.environment import MnoteEnvironment, pass_env, echo_line


@click.command(name="created")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@pass_env
def fix_created(env: MnoteEnvironment, files: List, n: Optional[int]):
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
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
                    converted = DateTime.strptime(long_stamp[0], ID_TIME_FORMAT)
                    got_long_stamp = True
                except ValueError:
                    echo_line(" * file had long-stamp but it ",  style.warning("didn't parse to a valid date/time"))
                    continue

            if got_long_stamp:
                time_stamp = converted.replace(tzinfo=env.note_builder.local_zone)
                echo_line(" * found timestamp in file name: ", style.visible(f"{time_stamp}"))
                changes.append((note, time_stamp))

            else:
                c_time, is_created = file_c_time(note.file_path)
                c_time = c_time.replace(tzinfo=env.note_builder.local_zone)
                extract_mode = 'created' if is_created else 'last modified'
                echo_line(f" * extracted ", style.visible(extract_mode), " timestamp from file system: ",
                          style.visible(f"{c_time}"))
                changes.append((note, c_time))

    echo_line()
    if not changes:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note, value in changes:
            note_with_content = env.note_builder.load_note(note.file_path)
            note_with_content.info.created = value
            with env.provider.write_file(note.file_path) as handle:
                handle.write(note_with_content.to_file_text())
    else:
        echo_line(style.fail("User rejected changes"))


