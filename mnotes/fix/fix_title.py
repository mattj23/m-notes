"""
    Fix missing title metadata
"""
import re
import click
from typing import List, Optional

from .common import echo_problem_title, load_working
from mnotes.notes.checks import note_checks
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

header_pattern = re.compile("^# (.*)")


@click.command(name="title")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
@pass_env
def fix_title(env: MnoteEnvironment, files: List[click.Path], n: Optional[int]):
    index = env.index_of_cwd

    working = load_working(index, env.cwd, files)
    if working is None:
        return

    style = env.config.styles

    changes = []
    for note in working:
        if n is not None and len(changes) >= n:
            break

        if note_checks["title"]["check"](note):
            echo_problem_title("Missing Title", note)

            note_with_content = env.note_builder.load_note(note.file_path)
            content = note_with_content.content.strip().split("\n")
            header = header_pattern.findall(content[0])
            if header:
                title = header[0].strip()
                echo_line(" * header found in content ", style.visible(f"{title}"))
                changes.append((note, title))
            else:
                echo_line(" * ", style.warning("no header"), " found in context")

    echo_line()
    if not changes:
        echo_line(click.style("There were no potential fixes found", bold=True))
        return

    if click.confirm(click.style(f"Apply these {len(changes)} changes?", bold=True)):
        echo_line(style.success("User accepted changes"))
        for note, new_title in changes:
            note_with_content = env.note_builder.load_note(note.file_path)
            note_with_content.info.title = new_title
            with env.provider.write_file(note.file_path) as handle:
                handle.write(note_with_content.to_file_text())
    else:
        echo_line(style.fail("User rejected changes"))

