from copy import deepcopy
from typing import Dict

import pytest
from datetime import datetime as DateTime
from mnotes.notes.markdown_notes import Note, ID_TIME_FORMAT
from mnotes.utility.file_system import FileSystemProvider
from tests.test_fixes import transact_fixture, local_tz
from tests.tools.file_system_mocks import TestFileSystemProvider


def but_for(provider: TestFileSystemProvider, *args) -> Dict:
    d = deepcopy(provider.internal)
    for a in args:
        del d[a]
    return d


def test_simple_transaction_doesnt_change_data_in_index(transact_fixture):
    provider, index_builder, master = transact_fixture
    copy = deepcopy(provider)
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.author = "Replaced Author"
    t.add_change(f0, note)

    assert master.by_id["20240102080135"].author == "Alice Allison"
    assert index_builder.note_builder.load_note(f0).info.author == "Alice Allison"
    assert but_for(provider) == but_for(copy)


def test_simple_transaction_fetches_updated_data(transact_fixture):
    provider, index_builder, master = transact_fixture
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.author = "Replaced Author"
    t.add_change(f0, note)

    note_info2 = t.get_note_info_state(f0)
    note2 = t.get_note_state(f0)
    assert note_info2.author == "Replaced Author"
    assert note2.info.author == "Replaced Author"


def test_simple_transaction_changing_fetched_does_not_update(transact_fixture):
    provider, index_builder, master = transact_fixture
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.author = "Replaced Author"
    t.add_change(f0, note)

    note_info2 = t.get_note_info_state(f0)
    note2 = t.get_note_state(f0)

    note_info2.author = "changed"
    note2.info.author = "changed"

    assert t.get_note_info_state(f0).author == "Replaced Author"
    assert t.get_note_state(f0).info.author == "Replaced Author"


def test_simple_transaction_applies(transact_fixture):
    provider, index_builder, master = transact_fixture
    copy = deepcopy(provider)
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.author = "Replaced Author"
    t.add_change(f0, note)
    master.apply_transaction(t)
    master.load_all()
    assert master.by_id["20240102080135"].author == "Replaced Author"
    assert but_for(copy, f0) == but_for(provider, f0)


def test_staged_transaction_applies(transact_fixture):
    provider, index_builder, master = transact_fixture
    copy = deepcopy(provider)
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.author = "Replaced Author"
    t.add_change(f0, note)

    f1 = "/alpha/note-01.md"
    note = t.get_note_state(f1)
    note.info.id = "12345678901234"
    note.info.title = "Replaced Title"
    t.add_change(f1, note)

    master.apply_transaction(t)
    master.load_all()
    assert master.by_id["20240102080135"].author == "Replaced Author"
    assert master.by_id["12345678901234"].title == "Replaced Title"
    assert "19990907012114" not in master.all_ids
    assert but_for(copy, f0, f1) == but_for(provider, f0, f1)


def test_transaction_build_errors_on_conflict(transact_fixture):
    provider, index_builder, master = transact_fixture
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/alpha/note-00.md"
    note = t.get_note_state(f0)
    note.info.id = "12345678901234"
    t.add_change(f0, note)

    f1 = "/alpha/note-01.md"
    note = t.get_note_state(f1)
    note.info.id = "12345678901234"
    note.info.title = "Replaced Title"
    assert not t.verify(f1, note)

    with pytest.raises(ValueError):
        t.add_change(f1, note)


def test_hetrogenous_transaction_with_move(transact_fixture):
    provider, index_builder, master = transact_fixture
    copy = deepcopy(provider)
    master.load_all()
    t = master.create_empty_transaction()

    f0 = "/fix/timestamp-none.md"
    note = t.get_note_state(f0)
    note.info.created = provider.file_c_time(f0)[0]
    note.info.author = "Replaced Author"
    fr = "/alpha/note-renamed.md"
    note.info.file_path = fr
    t.add_change(f0, note)

    f1 = "/alpha/note-01.md"
    note = t.get_note_state(f1)
    note.info.id = "12345678901234"
    note.info.title = "Replaced Title"
    t.add_change(f1, note)

    note = t.get_note_state(f0)
    note.info.id = note.info.created.strftime(ID_TIME_FORMAT)
    t.add_change(f0, note)

    master.apply_transaction(t)
    master.load_all()

    assert master.by_id["12345678901234"].title == "Replaced Title"
    assert "19990907012114" not in master.all_ids

    assert f0 not in master.by_path
    assert master.by_path[fr].author == "Replaced Author"
    assert master.by_path[fr].id == "20150430174927"
    assert master.by_path[fr].created == DateTime(2015, 4, 30, 17, 49, 27)
    assert but_for(copy, f0, f1) == but_for(provider, f1, fr)

