"""
    Fix IDs Mode
"""
import click
from typing import List, Optional, Set

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

from .common import echo_problem_title
from mnotes.notes.markdown_notes import load_all_notes, get_existing_ids, NoteMetadata
from mnotes.notes.checks import note_checks, long_stamp_format

from mnotes.environment import MnoteEnvironment, pass_env, echo_line


@click.command(name="id")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--resolve", "resolve", flag_value=True,
              help="Attempt to resolve ID conflicts by adjusting creation time")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_id(env: MnoteEnvironment, files: List[click.Path], n: Optional[int], resolve: bool):
    all_notes = load_all_notes(env.cwd)
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

            new_id = note.created.strftime(long_stamp_format)
            has_conflict = False
            if new_id in all_ids:
                echo_line(f" * cannot create ID {new_id} because it ",
                          style.warning("conflicts with an existing ID"), " in the corpus")
                has_conflict = True

            if new_id in new_ids:
                echo_line(f" * cannot create ID {new_id} because it ", style.warning("conflicts with a proposed ID"))
                has_conflict = True

            if has_conflict:
                if resolve:
                    combined = all_ids.copy()
                    combined.update(new_ids)
                    new_c_time = suggest_conflict_fix(note, combined)
                    offset = abs((new_c_time - note.created).seconds)
                    new_id = new_c_time.strftime(long_stamp_format)

                    echo_line(f" * propose changing note creation time by ",
                              style.visible("{offset} seconds to {new_c_time}"))
                    echo_line(" * new ID would then be ", style.visible("{new_id}"))
                    changes.append((note, new_id, new_c_time))
                    new_ids.add(new_id)
                    continue

                else:
                    conflicts += 1
                    continue

            echo_line(" * id from creation timestamp = ", style.visible("{new_id}"))
            new_ids.add(new_id)
            changes.append((note, new_id, None))

    click.echo()
    if conflicts > 0:
        click.echo(style.warning(f"There were {conflicts} conflicts. Consider running with the --resolve option."))

    if not changes:
        click.echo(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        click.echo(style.success("User accepted changes"))
        for note, value, new_timestamp in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.id = value
            if new_timestamp is not None:
                note_with_content.created = new_timestamp
            note_with_content.save_file()

    else:
        click.echo(style.fail("User rejected changes"))


def suggest_conflict_fix(note: NoteMetadata, existing_ids: Set[str]) -> DateTime:
    proposed = note.created
    while proposed.strftime(long_stamp_format) in existing_ids:
        proposed = proposed + TimeDelta(seconds=1)

    return proposed
