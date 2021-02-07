"""
    Fix IDs Mode
"""

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

from modes.common import arg_to_working_list
from notes.markdown_notes import load_all_notes, get_existing_ids, NoteMetadata
from notes.checks import note_checks, long_stamp_format

from typing import Set


def mode(working_path: str, fix_arg: str, resolve: bool):
    all_notes = load_all_notes(working_path)
    count, working = arg_to_working_list(fix_arg, "", all_notes)
    if working is None:
        return

    try:
        all_ids = get_existing_ids(all_notes)
    except ValueError as e:
        print(f"Error: {e}")
        return

    changes = []
    new_ids: Set[str] = set()
    conflicts = 0
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["id"]["check"](note):
            print("\nMissing Note ID")
            print(f" * title =    {note.title} ")
            print(f" * filename = {note.file_name}")

            if note.created is None:
                print(f" * cannot generate ID for this note, it has no creation time!")
                continue

            new_id = note.created.strftime(long_stamp_format)
            has_conflict = False
            if new_id in all_ids:
                print(f" * cannot create ID {new_id} because it conflicts with an existing ID in the corpus")
                has_conflict = True

            if new_id in new_ids:
                print(f" * cannot create ID {new_id} because it conflicts with another proposed ID ")
                has_conflict = True

            if has_conflict:
                if resolve:
                    combined = all_ids.copy()
                    combined.update(new_ids)
                    new_c_time = suggest_conflict_fix(note, combined)
                    offset = abs((new_c_time - note.created).seconds)
                    new_id = new_c_time.strftime(long_stamp_format)

                    print(f" * propose changing note creation time by {offset} seconds to {new_c_time}")
                    print(f" * new ID would then be {new_id}")
                    changes.append((note, new_id, new_c_time))
                    new_ids.add(new_id)
                    continue

                else:
                    conflicts += 1
                    continue

            print(f" * id from creation timestamp = {new_id}")
            new_ids.add(new_id)
            changes.append((note, new_id, None))

    if conflicts > 0:
        print(f"\nThere were {conflicts} conflicts. Consider running with the --resolve option.")

    if not changes:
        print("\nNo changes to be made")
        return

    response = input(f"\nApply {len(changes)} changes? [yes/no]: ").strip().lower()
    if response in ['y', 'yes']:
        for note, value, new_timestamp in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.id = value
            if new_timestamp is not None:
                note_with_content.created = new_timestamp
            note_with_content.save_file()


def suggest_conflict_fix(note: NoteMetadata, existing_ids: Set[str]) -> DateTime:
    proposed = note.created

    while proposed.strftime(long_stamp_format) in existing_ids:
        proposed = proposed + TimeDelta(seconds=1)

    return proposed


