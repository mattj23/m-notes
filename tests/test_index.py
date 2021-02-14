import pytest
from copy import deepcopy
from dateutil import tz
import tests.tools.sample_data as sample
from tests.tools.file_system_mocks import TestFileSystemProvider

from mnotes.notes.markdown_notes import NoteBuilder, MetaData
from mnotes.notes.index import IndexBuilder, NoteIndex, GlobalIndices

local_tz = tz.gettz("Africa/Harare")


@pytest.fixture
def five_normal_notes():
    provider = TestFileSystemProvider(deepcopy(sample.INDEX_FIVE_NORMAL_NOTES))
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    return provider, index_builder


@pytest.fixture
def dual_folders():
    d1 = deepcopy(sample.INDEX_FIVE_NORMAL_NOTES)
    d2 = deepcopy(sample.INDEX_WITH_MISSING_ATTRS)
    d1.update(d2)
    provider = TestFileSystemProvider(d1)
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    return provider, index_builder


@pytest.fixture
def conflict_data():
    provider = TestFileSystemProvider(deepcopy(sample.INDEX_WITH_CONFLICTS))
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    return provider, index_builder


def test_index_loads_from_provider(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")

    assert "test" == index.name
    assert "/" == index.path
    assert sorted(f"/home/note-{i:02d}.md" for i in range(5)) == sorted(n.file_path for n in index.notes.values())
    assert sorted(f"/home/note-{i:02d}.md" for i in range(5)) == sorted(f.full_path for f in index.files.values())


def test_index_serialize_round_trip(five_normal_notes):
    provider, index_builder = five_normal_notes

    index = index_builder.create("test", "/")
    serialized = index.serialize()

    loaded = NoteIndex.deserialize(serialized)

    assert index.name == loaded.name
    assert index.path == loaded.path
    assert index.files == loaded.files
    assert index.notes == loaded.notes


def test_index_detect_files_removed(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")
    del provider.internal["/home/note-00.md"]
    index_builder.update(index)

    assert sorted(f"/home/note-{i:02d}.md" for i in range(1, 5)) == sorted(n.file_path for n in index.notes.values())
    assert sorted(f"/home/note-{i:02d}.md" for i in range(1, 5)) == sorted(f.full_path for f in index.files.values())


def test_index_detect_files_added(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")
    provider.internal["/home/note-05.md"] = {
        "content": sample.MD_SAMPLE_NOTE_0,
        "modified": 10
    }
    index_builder.update(index)

    assert sorted(f"/home/note-{i:02d}.md" for i in range(6)) == sorted(n.file_path for n in index.notes.values())
    assert sorted(f"/home/note-{i:02d}.md" for i in range(6)) == sorted(f.full_path for f in index.files.values())
    assert index.notes["/home/note-05.md"].author == "Robert Robertson"
    assert index.notes["/home/note-05.md"].id == "20210213160525"


def test_index_detect_files_changed_checksums(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")

    # Change one letter in the author's name but nothing in the time or size and update the index
    text: str = provider.internal["/home/note-00.md"]["content"]
    provider.internal["/home/note-00.md"]["content"] = text.replace("Eva Evanston", "Eve Evanston")
    index_builder.update(index, True)

    assert "Eve Evanston" == index.notes["/home/note-00.md"].author


def test_index_detect_files_changed_size(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")

    # Change one letter in the author's name and update the index
    text: str = provider.internal["/home/note-00.md"]["content"]
    provider.internal["/home/note-00.md"]["content"] = text.replace("Eva Evanston", "Evan Evanston")
    index_builder.update(index)

    assert "Evan Evanston" == index.notes["/home/note-00.md"].author


def test_index_detect_files_changed_timestamp(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")

    # Change one letter in the author's name and update the index
    text: str = provider.internal["/home/note-00.md"]["content"]
    provider.internal["/home/note-00.md"]["content"] = text.replace("Eva Evanston", "Eve Evanston")
    provider.internal["/home/note-00.md"]["modified"] += 1
    index_builder.update(index)

    assert "Eve Evanston" == index.notes["/home/note-00.md"].author


def test_index_detect_all_changes(five_normal_notes):
    provider, index_builder = five_normal_notes
    index = index_builder.create("test", "/")
    del provider.internal["/home/note-00.md"]
    provider.internal["/home/note-05.md"] = {
        "content": sample.MD_SAMPLE_NOTE_0,
        "modified": 10
    }
    text = provider.internal["/home/note-01.md"]["content"]
    provider.internal["/home/note-01.md"]["content"] = text.replace("title: In magna etiam",
                                                                    "title: I edited this")
    index_builder.update(index)
    assert "I edited this" == index.notes["/home/note-01.md"].title
    assert sorted(f"/home/note-{i:02d}.md" for i in range(1, 6)) == sorted(n.file_path for n in index.notes.values())
    assert sorted(f"/home/note-{i:02d}.md" for i in range(1, 6)) == sorted(f.full_path for f in index.files.values())


def test_global_build_index(dual_folders):
    provider, index_builder = dual_folders

    directory = {
        "home": {"path": "/home"},
        "alpha": {"path": "/alpha"}
    }

    master = GlobalIndices(index_builder, directory=directory)
    master.load_all()

    assert len(master.indices) == 2
    assert len(master.by_id) == 10
    assert all(n.state == MetaData.OK for n in master.by_id.values())
    assert master.indices["alpha"].notes["/alpha/missing-id.md"].state == MetaData.NO_ID
    assert master.indices["alpha"].notes["/alpha/missing-created.md"].state == MetaData.NO_ID


def test_global_index_detects_conflicts(conflict_data):
    provider, index_builder = conflict_data
    directory = {
        "bravo": {"path": "/bravo"},
        "charlie": {"path": "/charlie"},
        "delta": {"path": "/delta"}
    }
    master = GlobalIndices(index_builder, directory=directory)
    master.load_all()

    assert len(master.by_id) == 9
    assert ["20071116151627"] == list(master.conflicts.keys())
    assert all(n.state == MetaData.CONFLICT for n in master.conflicts["20071116151627"])
    assert all(n.state == MetaData.OK for n in master.by_id.values())




