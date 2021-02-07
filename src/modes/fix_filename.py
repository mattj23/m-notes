"""
    Fix IDs Mode
"""
import os
import shutil
from modes.common import arg_to_working_list
from notes.markdown_notes import NoteMetadata
from notes.checks import note_checks, long_stamp_format


def mode(working_path: str, fix_arg: str):
    count, working = arg_to_working_list(fix_arg, working_path)
    if working is None:
        return

    changes = []
    proposed_paths = set()
    conflicts = 0
    for note in working:
        if count is not None and len(changes) >= count:
            break

        if note_checks["id_filename"]["check"](note):
            print("\nID Missing from Filename")
            print(f" * title =    {note.title} ")
            print(f" * filename = {note.file_name}")

            if note.id is None:
                print(f" * cannot add ID to filename because note does not have an ID!")
                continue

            base_name, extension = os.path.splitext(note.file_name)
            directory = os.path.dirname(note.file_path)
            proposed_filename = f"{note.id}_{base_name.strip()}{extension}"
            proposed_path = os.path.join(directory, proposed_filename)

            if os.path.exists(proposed_path):
                print(f" * cannot rename to '{proposed_path}' because another file already exists there")
                conflicts += 1
                continue

            if proposed_path in proposed_paths:
                print(f" * cannot rename to '{proposed_path}' because another file with that name has already been "
                      f"proposed")
                conflicts += 1
                continue

            print(f" * proposed new filename: {proposed_filename}")
            changes.append((note, proposed_path))

    if conflicts > 0:
        print(f"\nThere were {conflicts} conflicts.")

    if not changes:
        print("\nNo changes to be made")
        return

    response = input(f"\nApply {len(changes)} changes? [yes/no]: ").strip().lower()
    if response in ['y', 'yes']:
        for note, value in changes:
            print(f"\nMoving {note.title}")
            print(f" -> from {note.file_path}")
            print(f" -> to {value}")
            shutil.move(note.file_path, value)



