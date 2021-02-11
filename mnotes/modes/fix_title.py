"""
    Fix missing title metadata
"""
import re
from typing import List, Optional

from mnotes.notes.markdown_notes import NoteMetadata, local_time_zone, load_all_notes
from mnotes.notes.checks import note_checks, long_stamp_pattern, from_timestamp_id, file_c_time

header_pattern = re.compile("^# (.*)")


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

        if note_checks["title"]["check"](note):
            print("\nMissing Note Title")
            print(f" * title =    {note.title} ")
            print(f" * filename = {note.file_name}")

            note_with_content = NoteMetadata(note.file_path, store_content=True)
            content = note_with_content.content.strip().split("\n")
            header = header_pattern.findall(content[0])
            if header:
                title = header[0].strip()
                print(f" * header found in content: '{title}'")
                changes.append((note, title))
            else:
                print(f" * no header found in content")

    if not changes:
        print("\nNo actionable headers found")
        return

    response = input("\nApply changes? [yes/no]: ").strip().lower()
    if response in ['y', 'yes']:
        print("\nUser accepted changes")
        for note, new_title in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.title = new_title
            note_with_content.save_file()
    else:
        print("\nUser rejected changes")


