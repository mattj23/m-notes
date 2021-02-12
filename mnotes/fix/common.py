import os
import click
from mnotes.notes.markdown_notes import NoteMetadata, load_all_notes
from typing import Optional, Tuple, List, Set, Callable


def echo_problem_title(issue: str, note: NoteMetadata):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


def parse_to_int(text: str) -> Optional[int]:
    try:
        return int(text.strip())
    except:
        return None


def arg_to_working_list(arg_contents: str, working_path: str, all_notes: Optional[List[NoteMetadata]] = None) -> \
        Tuple[Optional[int], Optional[List[NoteMetadata]]]:
    def get_all():
        return load_all_notes(working_path) if all_notes is None else list(all_notes)

    if parse_to_int(arg_contents):
        count = parse_to_int(arg_contents)
        return count, get_all()
    elif arg_contents.strip():
        if not os.path.exists(arg_contents):
            print(f"Error: file '{arg_contents}' could not be found! Aborting!")
            return None, None
        return None, [NoteMetadata(arg_contents)]
    else:
        return None, get_all()


def check_for_missing_attr(notes: List[NoteMetadata], checker: Callable[[NoteMetadata], bool]) -> List[NoteMetadata]:
    missing = []
    for note in notes:
        if checker(note):
            missing.append(note)
    return missing
