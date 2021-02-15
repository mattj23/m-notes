"""
    Fix IDs Mode
"""
import click
from typing import List, Optional, Set, Callable

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

from .common import echo_problem_title, load_working
from mnotes.notes.checks import note_checks

from mnotes.environment import MnoteEnvironment, pass_env, echo_line, ID_TIME_FORMAT
from ..notes.markdown_notes import NoteInfo


@click.command(name="id")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--resolve", "resolve", flag_value=True,
              help="Attempt to resolve ID conflicts by adjusting creation time")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_id(env: MnoteEnvironment, files: List[click.Path], n: Optional[int], resolve: bool):
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
    if working is None:
        return

    style = env.config.styles

    changes = []
    new_ids: Set[str] = set()
    conflicts = 0
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["id"]["check"](note):
            echo_problem_title("Missing ID", note)

            if note.created is None:
                echo_line(" * cannot generate ID for this note, it has ", style.warning("no creation time"))
                continue

            new_id = note.created.strftime(ID_TIME_FORMAT)
            has_conflict = False
            if env.global_index.has_id(new_id):
                echo_line(f" * cannot create ID {new_id} because it ",
                          style.warning("conflicts with an existing ID"), " in the global directory")
                has_conflict = True

            if new_id in new_ids:
                echo_line(f" * cannot create ID {new_id} because it ", style.warning("conflicts with a proposed ID"))
                has_conflict = True

            if has_conflict:
                if resolve:
                    new_c_time = suggest_conflict_fix(note, lambda id_: env.global_index.has_id(id_) or id_ in new_ids)
                    offset = abs((new_c_time - note.created).seconds)
                    new_id = new_c_time.strftime(ID_TIME_FORMAT)

                    echo_line(f" * propose changing note creation time by ",
                              style.visible(f"{offset} seconds to {new_c_time}"))
                    echo_line(" * new ID would then be ", style.visible(f"{new_id}"))
                    changes.append((note, new_id, new_c_time))
                    new_ids.add(new_id)
                    continue

                else:
                    conflicts += 1
                    continue

            echo_line(" * id from creation timestamp = ", style.visible(f"{new_id}"))
            new_ids.add(new_id)
            changes.append((note, new_id, None))

    echo_line()
    if conflicts > 0:
        echo_line(style.warning(f"There were {conflicts} conflicts. Consider running with the --resolve option."))

    if not changes:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note, value, new_timestamp in changes:
            note_with_content = env.note_builder.load_note(note.file_path)
            note_with_content.info.id = value
            if new_timestamp is not None:
                note_with_content.info.created = new_timestamp
            with env.provider.write_file(note.file_path) as handle:
                handle.write(note_with_content.to_file_text())
    else:
        echo_line(style.fail("User rejected changes"))


def suggest_conflict_fix(note: NoteInfo, check: Callable[[str], bool]) -> DateTime:
    proposed = note.created
    while check(proposed.strftime(ID_TIME_FORMAT)):
        proposed = proposed + TimeDelta(seconds=1)

    return proposed
