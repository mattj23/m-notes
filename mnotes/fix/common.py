import os
import click

from mnotes.environment import Styles
from mnotes.notes.markdown_notes import NoteInfo, LONG_STAMP_PATTERN, ID_TIME_FORMAT, NoteBuilder
from mnotes.notes.index import NoteIndex
from typing import Optional, Tuple, List, Set, Callable
from mnotes.utility.change import NoteChange, NoteChanger, ChangeTransaction, TryChangeResult

from datetime import datetime as DateTime
from datetime import tzinfo


def echo_problem_title(issue: str, note: NoteInfo):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


def file_c_time(file_path: str) -> Tuple[DateTime, bool]:
    """
    Get the file creation time from the operating system. This will not return good results on Linux
    :param file_path:
    :return: a datetime and a bool indicating whether it was the creation time or modification time returned
    """
    f_stat = os.stat(file_path)
    try:
        c_time = DateTime.fromtimestamp(f_stat.st_birthtime)
        return c_time, True
    except AttributeError:
        c_time = DateTime.fromtimestamp(f_stat.st_mtime)
    return c_time, False


def load_working(index: NoteIndex, path: str, files: List) -> List[NoteInfo]:
    if not files:
        return index.notes_in_path(path)
    else:
        abs_paths = map(os.path.abspath, files)
        return [index.notes[f] for f in abs_paths if f in index.notes]


class Fixer(NoteChanger):
    def __init__(self, builder: NoteBuilder, style: Styles = None):
        self.styles = style
        self.builder = builder

    def vis(self, text: str) -> str:
        if self.styles:
            return self.styles.visible(text)
        return text

    def success(self, text: str) -> str:
        if self.styles:
            return self.styles.success(text)
        return text

    def fail(self, text: str) -> str:
        if self.styles:
            return self.styles.fail(text)
        return text

    def warn(self, text: str) -> str:
        if self.styles:
            return self.styles.warning(text)
        return text


class CreationFixer(Fixer):
    def __init__(self, builder: NoteBuilder, local_zone: tzinfo, style: Styles = None):
        super().__init__(builder, style)
        self.local = local_zone

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []

        long_stamp = LONG_STAMP_PATTERN.findall(note_info.file_name)
        got_long_stamp = False
        converted = None
        if long_stamp:
            try:
                converted = DateTime.strptime(long_stamp[0], ID_TIME_FORMAT)
                got_long_stamp = True
            except ValueError:
                desc.append([" * file had long-stamp but it ", self.warn("didn't parse to a valid date/time")])
                return TryChangeResult.failed(desc)

        if got_long_stamp:
            time_stamp = converted.replace(tzinfo=self.local)
            desc.append([" * found timestamp in file name: ", self.vis(f"{time_stamp}")])
            change = NoteChange(note_info, self, data=time_stamp)
            return TryChangeResult.ok(change, desc)

        else:
            c_time, is_created = file_c_time(note_info.file_path)
            c_time = c_time.replace(tzinfo=self.local)
            extract_mode = 'created' if is_created else 'last modified'
            desc.append([f" * extracted ", self.vis(extract_mode), " timestamp from file system: ",
                         self.vis(f"{c_time}")])
            change = NoteChange(note_info, self, data=c_time)
            return TryChangeResult.ok(change, desc)

    def apply_change(self, change: NoteChange):
        note_with_content = self.builder.load_note(change.note_info.file_path)
        note_with_content.info.created = change.change_data
        with self.builder.provider.write_file(change.note_info.file_path) as handle:
            handle.write(note_with_content.to_file_text())


class IdFixer(Fixer):
    def __init__(self, builder: NoteBuilder, local_zone: tzinfo, style: Styles = None):
        super().__init__(builder, style)
        self.local = local_zone

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []

        long_stamp = LONG_STAMP_PATTERN.findall(note_info.file_name)
        got_long_stamp = False
        converted = None
        if long_stamp:
            try:
                converted = DateTime.strptime(long_stamp[0], ID_TIME_FORMAT)
                got_long_stamp = True
            except ValueError:
                desc.append([" * file had long-stamp but it ", self.warn("didn't parse to a valid date/time")])
                return TryChangeResult.failed(desc)

        if got_long_stamp:
            time_stamp = converted.replace(tzinfo=self.local)
            desc.append([" * found timestamp in file name: ", self.vis(f"{time_stamp}")])
            change = NoteChange(note_info, self, data=time_stamp)
            return TryChangeResult.ok(change, desc)

        else:
            c_time, is_created = file_c_time(note_info.file_path)
            c_time = c_time.replace(tzinfo=self.local)
            extract_mode = 'created' if is_created else 'last modified'
            desc.append([f" * extracted ", self.vis(extract_mode), " timestamp from file system: ",
                         self.vis(f"{c_time}")])
            change = NoteChange(note_info, self, data=c_time)
            return TryChangeResult.ok(change, desc)

    def apply_change(self, change: NoteChange):
        note_with_content = self.builder.load_note(change.note_info.file_path)
        note_with_content.info.created = change.change_data
        with self.builder.provider.write_file(change.note_info.file_path) as handle:
            handle.write(note_with_content.to_file_text())
