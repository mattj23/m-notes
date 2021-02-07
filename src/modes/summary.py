"""
    Summary mode, which displays an overview of the corpus
"""
import time
from modes.common import check_for_missing_attr
from notes.markdown_notes import load_all_notes
from notes.checks import note_checks


def mode(working_path: str, summary_count: int):
    start_time = time.time()
    print(f"\nRunning M-Notes in Summary Mode")
    print("========================================================")
    print(f" * working directory: {working_path}")

    notes = load_all_notes(working_path)
    print(f" * total notes in corpus: {len(notes)}")
    order = ["created", "id", "id_filename"]

    for check in [note_checks[o] for o in order]:
        missing = check_for_missing_attr(notes, check["check"])
        if missing:
            print(f"\nFound {len(missing)} notes that are {check['description']}")
            for n in missing[:summary_count]:
                print(f" -> {n.file_path}")
            remaining = len(missing) - summary_count
            if remaining > 0:
                print(f" -> ... and {remaining} more")

    end_time = time.time()
    print(f"\nTook {end_time - start_time:0.2f} seconds")
