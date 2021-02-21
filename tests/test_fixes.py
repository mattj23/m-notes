from copy import deepcopy

import pytest
import tests.tools.sample_data as sample
from mnotes.notes.index import IndexBuilder
from mnotes.notes.markdown_notes import NoteBuilder
from mnotes.utility.change import ChangeTransaction
from tests.test_index import local_tz

from mnotes.fix.common import CreationFixer
from mnotes.notes.markdown_notes import ID_TIME_FORMAT
from tests.tools.file_system_mocks import TestFileSystemProvider
from datetime import datetime as DateTime


@pytest.fixture
def check_fixture():
    d1 = deepcopy(sample.INDEX_FOR_FIXERS)
    d2 = deepcopy(sample.INDEX_WITH_MISSING_ATTRS)
    d1.update(d2)
    provider = TestFileSystemProvider(d1)
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    return provider, index_builder


def test_created_check_false(check_fixture):
    provider, builder = check_fixture
    note = builder.note_builder.load_note("/alpha/note-00.md")
    fixer = CreationFixer(builder.note_builder, local_zone=local_tz)

    assert not fixer.check(note.info)


def test_created_check_true(check_fixture):
    provider, builder = check_fixture
    note = builder.note_builder.load_note("/alpha/missing-created.md")
    fixer = CreationFixer(builder.note_builder, local_zone=local_tz)

    assert fixer.check(note.info)


def test_created_invalid_parse_long_stamp(check_fixture):
    provider, builder = check_fixture
    note = builder.note_builder.load_note("/fix/timestamp-wrong-20130434025112.md")
    fixer = CreationFixer(builder.note_builder, local_zone=local_tz)
    result = fixer.try_change(note.info, ChangeTransaction())

    assert result.is_failed


def test_created_got_long_stamp(check_fixture):
    provider, builder = check_fixture
    note = builder.note_builder.load_note("/fix/timestamp-legit-20031117110124.md")
    fixer = CreationFixer(builder.note_builder, local_zone=local_tz)
    result = fixer.try_change(note.info, ChangeTransaction())

    fixer.apply_change(result.change)
    note2 = builder.note_builder.load_note("/fix/timestamp-legit-20031117110124.md")

    assert result.is_ok
    assert note2.info.created.strftime(ID_TIME_FORMAT) == "20031117110124"


def test_created_read_file_time(check_fixture):

    provider, builder = check_fixture
    note = builder.note_builder.load_note("/fix/timestamp-none.md")
    fixer = CreationFixer(builder.note_builder, local_zone=local_tz)
    result = fixer.try_change(note.info, ChangeTransaction())

    fixer.apply_change(result.change)
    note2 = builder.note_builder.load_note("/fix/timestamp-none.md")

    assert result.is_ok
    assert note2.info.created == DateTime(2015, 4, 30, 17, 49, 27, tzinfo=local_tz)
