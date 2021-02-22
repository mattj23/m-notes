from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Tuple

import pytest
import tests.tools.sample_data as sample
from mnotes.notes.index import IndexBuilder, GlobalIndices
from mnotes.notes.markdown_notes import NoteBuilder, NoteInfo
from mnotes.utility.change import ChangeTransaction
from tests.test_index import local_tz

from mnotes.fix.common import CreationFixer, IdFixer, AuthorFixer, TitleFixer, FilenameFixer
from mnotes.notes.markdown_notes import ID_TIME_FORMAT
from tests.tools.file_system_mocks import TestFileSystemProvider
from datetime import datetime as DateTime


@dataclass
class Fixture:
    index_builder: IndexBuilder
    provider: TestFileSystemProvider
    master: GlobalIndices
    transact: ChangeTransaction


@pytest.fixture
def fixture() -> Fixture:
    d1 = deepcopy(sample.INDEX_FOR_FIXERS)
    d2 = deepcopy(sample.INDEX_WITH_MISSING_ATTRS)
    d1.update(d2)
    provider = TestFileSystemProvider(d1)
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    directory = {"alpha": {"path": "/alpha"}, "fix": {"path": "/fix"}}
    master = GlobalIndices(index_builder, directory=directory)
    master.load_all()
    transact = master.create_empty_transaction()
    return Fixture(index_builder, provider, master, transact)


def but_for(d: NoteInfo, key: str) -> Dict:
    if isinstance(d, NoteInfo):
        d2 = d.to_dict()
    else:
        d2 = deepcopy(d)
    del d2[key]
    return d2


def test_created_check_false(fixture):
    note = fixture.master.get_note_info("/alpha/note-00.md")
    fixer = CreationFixer(fixture.index_builder.note_builder, local_zone=local_tz)

    assert not fixer.check(note)


def test_created_check_true(fixture):
    note = fixture.master.get_note_info("/alpha/missing-created.md")
    fixer = CreationFixer(fixture.index_builder.note_builder, local_zone=local_tz)

    assert fixer.check(note)


def test_created_invalid_parse_long_stamp(fixture):
    fixer = CreationFixer(fixture.index_builder.note_builder, local_zone=local_tz)
    result = fixer.try_change("/fix/timestamp-wrong-20130434025112.md", fixture.transact)

    assert result.is_failed


def test_created_got_long_stamp(fixture):
    file = "/fix/timestamp-legit-20031117110124.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = CreationFixer(fixture.index_builder.note_builder, local_zone=local_tz)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.created.strftime(ID_TIME_FORMAT) == "20031117110124"
    assert but_for(copy.info, "created") == but_for(note2.info, "created")
    assert copy.content == note2.content


def test_created_read_file_time(fixture):
    file = "/fix/timestamp-none.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = CreationFixer(fixture.index_builder.note_builder, local_zone=local_tz)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.created == DateTime(2015, 4, 30, 17, 49, 27, tzinfo=local_tz)
    assert but_for(copy.info, "created") == but_for(note2.info, "created")
    assert copy.content == note2.content


def test_id_check_true(fixture):
    note = fixture.master.get_note_info("/fix/missing-id-only.md")
    fixer = IdFixer(fixture.index_builder.note_builder, False)

    assert fixer.check(note)


def test_id_check_false(fixture):
    note = fixture.master.get_note_info("/alpha/note-00.md")
    fixer = IdFixer(fixture.index_builder.note_builder, False)

    assert not fixer.check(note)


def test_id_fix_simple(fixture):
    file = "/fix/missing-id-only.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = IdFixer(fixture.index_builder.note_builder, False)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.id == "20190728215833"
    assert but_for(copy.info, "id") == but_for(note2.info, "id")
    assert copy.content == note2.content


def test_id_refuse_existing_conflict(fixture):
    file = "/fix/missing-id-conflict.md"
    fixer = IdFixer(fixture.index_builder.note_builder, False)
    result = fixer.try_change(file, fixture.transact)

    assert result.is_failed


def test_id_resolve_existing_conflict(fixture):
    file = "/fix/missing-id-conflict.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = IdFixer(fixture.index_builder.note_builder, True)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.id == "20240102080136"
    assert note2.info.created == DateTime(2024, 1, 2, 8, 1, 36, tzinfo=local_tz)
    assert copy.content == note2.content


def test_filename_check_true(fixture):
    note = fixture.master.get_note_info("/alpha/note-00.md")
    fixer = FilenameFixer(fixture.index_builder.note_builder, False)

    assert fixer.check(note)


def test_filename_check_false(fixture):
    note = fixture.master.get_note_info("/fix/19931114154205-risus-libero-id.md")
    fixer = FilenameFixer(fixture.index_builder.note_builder, False)

    assert not fixer.check(note)


def test_filename_nothing_to_do(fixture):
    file = "/fix/19931114154205-risus-libero-id.md"
    fixer = FilenameFixer(fixture.index_builder.note_builder, True)
    result = fixer.try_change(file, fixture.transact)

    assert result.is_nothing


def test_filename_no_id(fixture):
    file = "/fix/missing-id-only.md"
    fixer = FilenameFixer(fixture.index_builder.note_builder, True)
    result = fixer.try_change(file, fixture.transact)

    assert result.is_failed


def test_filename_empty_title(fixture):
    file = "/fix/no-title-but-heading.md"
    fixer = FilenameFixer(fixture.index_builder.note_builder, True)
    result = fixer.try_change(file, fixture.transact)

    assert result.is_failed


def test_filename_simple_rename(fixture):
    file = "/alpha/note-00.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = FilenameFixer(fixture.index_builder.note_builder, False)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    fixture.master.load_all()
    assert file not in fixture.master.indices["alpha"].notes
    note2 = fixture.index_builder.note_builder.load_note("/alpha/20240102080135-note-00.md")

    assert result.is_ok
    assert but_for(note2.info, "file_path") == but_for(copy.info, "file_path")
    assert note2.content == copy.content


def test_filename_complete_rename(fixture):
    file = "/alpha/note-00.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = FilenameFixer(fixture.index_builder.note_builder, True)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    fixture.master.load_all()
    assert file not in fixture.master.indices["alpha"].notes
    note2 = fixture.index_builder.note_builder.load_note("/alpha/20240102080135-auctor-neque-vitae.md")

    assert result.is_ok
    assert but_for(note2.info, "file_path") == but_for(copy.info, "file_path")
    assert note2.content == copy.content


def test_author_check_true(fixture):
    note = fixture.master.get_note_info("/fix/author.md")
    fixer = AuthorFixer(fixture.index_builder.note_builder, "Irene Irenski")

    assert fixer.check(note)


def test_author_check_false(fixture):
    note = fixture.master.get_note_info("/alpha/note-00.md")
    fixer = AuthorFixer(fixture.index_builder.note_builder, "Irene Irenski")

    assert not fixer.check(note)


def test_author_fix(fixture):
    file = "/fix/author.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = AuthorFixer(fixture.index_builder.note_builder, "Irene Irenski")
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.author == "Irene Irenski"
    assert but_for(copy.info, "author") == but_for(note2.info, "author")
    assert copy.content == note2.content


def test_title_check_true(fixture):
    note = fixture.master.get_note_info("/fix/no-title-but-heading.md")
    fixer = TitleFixer(fixture.index_builder.note_builder)

    assert fixer.check(note)


def test_title_check_false(fixture):
    note = fixture.master.get_note_info("/alpha/note-00.md")
    fixer = TitleFixer(fixture.index_builder.note_builder)

    assert not fixer.check(note)


def test_title_fix_from_heading(fixture):
    file = "/fix/no-title-but-heading.md"
    copy = deepcopy(fixture.master.get_note(file))
    fixer = TitleFixer(fixture.index_builder.note_builder)
    result = fixer.try_change(file, fixture.transact)
    fixture.transact.add_change(file, result.change)
    fixture.master.apply_transaction(fixture.transact)

    note2 = fixture.index_builder.note_builder.load_note(file)

    assert result.is_ok
    assert note2.info.title == "At quis risus"
    assert but_for(copy.info, "title") == but_for(note2.info, "title")
    assert copy.content == note2.content


def test_title_cant_fix_no_heading(fixture):
    file = "/fix/no-title-or-heading.md"
    fixer = TitleFixer(fixture.index_builder.note_builder)
    result = fixer.try_change(file, fixture.transact)

    assert result.is_failed
