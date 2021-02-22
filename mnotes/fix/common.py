import os
import re
import click

from mnotes.environment import Styles
from mnotes.notes.markdown_notes import NoteInfo, LONG_STAMP_PATTERN, ID_TIME_FORMAT, NoteBuilder
from mnotes.notes.index import NoteIndex
from typing import Optional, Tuple, List, Set, Callable
from mnotes.utility.change import NoteChanger, ChangeTransaction, TryChangeResult

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from datetime import tzinfo

date_test_pattern = re.compile(r"^20[\d\.\-\_\s]*\d")
valid_chars_pattern = re.compile(r"[^a-z0-9]")
delete_words = {"on", "to", "the", "of", "and", "is", "at", "a", "an", "for", "in"}


def echo_problem_title(issue: str, note: NoteInfo):
    click.echo()
    click.echo(click.style(f"{issue}: ", bold=True), nl=False)
    click.echo(click.style(f"{note.title}", underline=True))
    click.echo(f" * filename = {note.file_name}")


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

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        note_with_content = transaction.get_note_state(original_path)
        content = note_with_content.content.strip().split("\n")
        header = self.header_pattern.findall(content[0])
        if header:
            title = header[0].strip()
            desc = [[" * header found in content ", self.vis(f"{title}")]]
            note_with_content.info.title = title
            return TryChangeResult.ok(note_with_content, desc)
        else:
            return TryChangeResult.failed([[" * ", self.warn("no header"), " found in context"]])


class AuthorFixer(Fixer):
    def __init__(self, builder: NoteBuilder, author: str, style: Styles = None):
        super().__init__(builder, style)
        self.author = author
        self.description = "missing an author"
        self.hint = "try the 'mnote fix author' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.author is None

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        desc = [[" * will set author to ", self.vis(f"'{self.author}'")]]
        note_with_content = transaction.get_note_state(original_path)
        note_with_content.info.author = self.author
        return TryChangeResult.ok(note_with_content, desc)


class CreationFixer(Fixer):
    def __init__(self, builder: NoteBuilder, local_zone: tzinfo, style: Styles = None):
        super().__init__(builder, style)
        self.local = local_zone
        self.description = "missing a creation time"
        self.hint = "try the 'mnote fix created' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.created is None

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []
        note = transaction.get_note_state(original_path)

        long_stamp = LONG_STAMP_PATTERN.findall(note.info.file_name)
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
            note.info.created = time_stamp
            return TryChangeResult.ok(note, desc)

        else:
            c_time, is_created = self.builder.provider.file_c_time(original_path)
            c_time = c_time.replace(tzinfo=self.local)
            extract_mode = 'created' if is_created else 'last modified'
            desc.append([f" * extracted ", self.vis(extract_mode), " timestamp from file system: ",
                         self.vis(f"{c_time}")])
            note.info.created = c_time
            return TryChangeResult.ok(note, desc)


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

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []
        note = transaction.get_note_state(original_path)
        new_id = note.info.created.strftime(ID_TIME_FORMAT)
        if new_id in transaction.ids:
            desc.append([f" * cannot create ID {new_id} because it ", self.warn("conflicts with an ID"),
                         " already in the global directory or the transaction"])

            if self.resolve:
                new_c_time = self._suggest_conflict_fix(note.info, lambda id_: id_ in transaction.ids)
                offset = abs((new_c_time - note.info.created).seconds)
                new_id = new_c_time.strftime(ID_TIME_FORMAT)

                desc.append([f" * propose changing note creation time by ",
                             self.vis(f"{offset} seconds to {new_c_time}")])
                desc.append([" * new ID would then be ", self.vis(f"{new_id}")])
                note.info.created = new_c_time
                note.info.id = new_id
                return TryChangeResult.ok(note, desc)

            else:
                return TryChangeResult.failed(desc)

        desc.append([" * id from creation timestamp = ", self.vis(f"{new_id}")])
        note.info.id = new_id
        return TryChangeResult.ok(note, desc)


class FilenameFixer(Fixer):
    def __init__(self, builder: NoteBuilder, complete: bool, style: Styles = None):
        super().__init__(builder, style)
        self.complete = complete
        self.description = "missing an id in the filename"
        self.hint = "try the 'mnote fix title' command"

    def check(self, note_info: NoteInfo) -> bool:
        return note_info.id is None or note_info.id not in note_info.file_name

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        desc = []
        note = transaction.get_note_state(original_path)

        if note.info.id is None:
            desc.append([" * cannot add ID to filename because ", self.warn("note does not have an ID!")])
            return TryChangeResult.failed(desc)

        if self.complete and note.info.title is None:
            desc.append([" * can't do a complete rename on this note because the ", self.warn("title is empty")])
            return TryChangeResult.failed(desc)

        directory = os.path.dirname(original_path)
        proposed_filename = complete_rewrite(note.info) if self.complete else prepend_id(note.info)

        if proposed_filename == note.info.file_name:
            desc.append([self.success(" * note already has the proposed name")])
            return TryChangeResult.nothing(desc)

        proposed_path = os.path.join(directory, proposed_filename)
        proposed_rel = os.path.relpath(proposed_path, start=os.curdir)
        note.info.file_path = proposed_path

        if not transaction.verify(original_path, note):
            desc.append([f" * cannot rename to '{proposed_rel}' because ", self.warn("another file already exists"),
                         " at that location"])
            return TryChangeResult.failed(desc)

        desc.append([" * proposed new filename: ", self.vis(f"{proposed_rel}")])
        return TryChangeResult.ok(note, desc)


def prepend_id(note: NoteInfo) -> str:
    base_name, extension = os.path.splitext(note.file_name)
    return f"{note.id}-{base_name.strip()}{extension}"


def add_words_up_to(length: int, word_set: List[str]) -> List[str]:
    working_words = list(word_set)
    built_words = []
    while working_words:
        active_word = working_words.pop(0)
        temp = built_words + [active_word]
        if len(temp) == 1 or len("-".join(temp)) < length:
            built_words = list(temp)
        else:
            return built_words
    return built_words


def complete_rewrite(note: NoteInfo) -> str:
    # Remove leading dates
    working = date_test_pattern.sub("", note.title.lower())
    working = valid_chars_pattern.sub(" ", working)
    all_words = working.split()
    cleaned_words = [word for word in all_words if word not in delete_words]

    enough_words = add_words_up_to(64, cleaned_words)
    working = "-".join(enough_words)

    return f"{note.id}-{working}.md"
