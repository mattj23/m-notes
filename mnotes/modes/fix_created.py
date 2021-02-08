"""
    Fix missing creation timestamps
"""
from typing import List, Optional

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
            print("\nMissing Creation Time")
            print(f" * title =    {note.title} ")
            print(f" * filename = {note.file_name}")

            long_stamp = long_stamp_pattern.findall(note.file_name)
            got_long_stamp = False
            if long_stamp:
                try:
                    converted = from_timestamp_id(long_stamp[0])
                    got_long_stamp = True
                except ValueError:
                    print(f" * file had long-stamp but it didn't parse to a valid date/time")

            if got_long_stamp:
                converted = local_time_zone.localize(converted)
                print(f" * found timestamp in file name: {long_stamp[0]}")
                print(f" * converts to {converted}")
                changes.append((note, converted))

            else:
                c_time, is_created = file_c_time(note.file_path)
                c_time = local_time_zone.localize(c_time)
                extract_mode = 'created' if is_created else 'last modified'
                print(f" * extracted {extract_mode} timestamp from file system: {c_time}")
                changes.append((note, c_time))

    if not changes:
        print("\nNo missing creation times found")
        return

    response = input("\nApply changes? [yes/no]: ").strip().lower()
    if response in ['y', 'yes']:
        print("\nUser accepted changes")
        for note, value in changes:
            note_with_content = NoteMetadata(note.file_path, store_content=True)
            note_with_content.created = value
            note_with_content.save_file()
    else:
        print("\nUser rejected changes")


