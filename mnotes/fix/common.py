import os
import re
import click

from mnotes.environment import Styles
from mnotes.notes.markdown_notes import NoteInfo, LONG_STAMP_PATTERN, ID_TIME_FORMAT, NoteBuilder
from mnotes.notes.index import NoteIndex
from typing import Optional, Tuple, List, Set, Callable
from mnotes.utility.change import NoteChange, NoteChanger, ChangeTransaction, TryChangeResult

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from datetime import tzinfo


def echo_problem_title(issue: str, note: NoteInfo):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


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
        self.description = ""
        self.hint = ""

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

    def check(self, note_info: NoteInfo) -> bool:
        pass



class TitleFixer(Fixer):
    def __init__(self, builder: NoteBuilder, style: Styles = None):
        super().__init__(builder, style)
        self.header_pattern = re.compile("^# (.*)")
        self.description = "missing the title in the metadata"
        self.hint = "try the 'mnote fix title' command"

    def check(self, note_info: NoteInfo) -> bool:
        return not note_info.title

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        note_with_content = self.builder.load_note(note_info.file_path)
        content = note_with_content.content.strip().split("\n")
        header = self.header_pattern.findall(content[0])
        if header:
            title = header[0].strip()
            desc = [[" * header found in content ", self.vis(f"{title}")]]
            change = NoteChange(note_info, self, data=title)
            return TryChangeResult.ok(change, desc)
        else:
            return TryChangeResult.failed([[" * ", self.warn("no header"), " found in context"]])

    def apply_change(self, change: NoteChange):
        note_with_content = self.builder.load_note(change.note_info.file_path)
        note_with_content.info.title = change.change_data
        with self.builder.provider.write_file(change.note_info.file_path) as handle:
            handle.write(note_with_content.to_file_text())


class AuthorFixer(Fixer):
    def __init__(self, builder: NoteBuilder, author: str, style: Styles = None):
        super().__init__(builder, style)
        self.author = author
        self.description = "missing an author"
        self.hint = "try the 'mnote fix author' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.author is None

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        desc = [[" * will set author to ", self.vis(f"'{self.author}'")]]
        change = NoteChange(note_info, self)
        return TryChangeResult.ok(change, desc)

    def apply_change(self, change: NoteChange):
        note_with_content = self.builder.load_note(change.note_info.file_path)
        note_with_content.info.author = self.author
        with self.builder.provider.write_file(change.note_info.file_path) as handle:
            handle.write(note_with_content.to_file_text())


class CreationFixer(Fixer):
    def __init__(self, builder: NoteBuilder, local_zone: tzinfo, style: Styles = None):
        super().__init__(builder, style)
        self.local = local_zone
        self.description = "missing a creation time"
        self.hint = "try the 'mnote fix created' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.created is None

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
            c_time, is_created = self.builder.provider.file_c_time(note_info.file_path)
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
    def __init__(self, builder: NoteBuilder, resolve: bool, style: Styles = None):
        super().__init__(builder, style)
        self.resolve = resolve
        self.description = "missing an id"
        self.hint = "try the 'mnote fix id' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.id is None

    @staticmethod
    def _suggest_conflict_fix(note: NoteInfo, check: Callable[[str], bool]) -> DateTime:
        proposed = note.created
        while check(proposed.strftime(ID_TIME_FORMAT)):
            proposed = proposed + TimeDelta(seconds=1)

        return proposed

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []

        new_id = note_info.created.strftime(ID_TIME_FORMAT)
        if new_id in transaction.ids:
            desc.append([f" * cannot create ID {new_id} because it ", self.warn("conflicts with an ID"),
                         " already in the global directory or the transaction"])

            if self.resolve:
                new_c_time = self._suggest_conflict_fix(note_info, lambda id_: id_ in transaction.ids)
                offset = abs((new_c_time - note_info.created).seconds)
                new_id = new_c_time.strftime(ID_TIME_FORMAT)

                desc.append([f" * propose changing note creation time by ",
                             self.vis(f"{offset} seconds to {new_c_time}")])
                desc.append([" * new ID would then be ", self.vis(f"{new_id}")])
                change = NoteChange(note_info, self, new_id=new_id, data=new_c_time)
                return TryChangeResult.ok(change, desc)

            else:
                return TryChangeResult.failed(desc)

        desc.append([" * id from creation timestamp = ", self.vis(f"{new_id}")])
        change = NoteChange(note_info, self, new_id=new_id)
        return TryChangeResult.ok(change, desc)

    def apply_change(self, change: NoteChange):
        note_with_content = self.builder.load_note(change.note_info.file_path)
        note_with_content.info.id = change.new_id
        if change.change_data is not None:
            note_with_content.info.created = change.change_data

        with self.builder.provider.write_file(change.note_info.file_path) as handle:
            handle.write(note_with_content.to_file_text())
