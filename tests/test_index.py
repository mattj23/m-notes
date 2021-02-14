import pytest
from copy import deepcopy
from dateutil import tz
import tests.tools.sample_data as sample
from tests.tools.file_system_mocks import TestFileSystemProvider

from mnotes.notes.markdown_notes import NoteBuilder
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


def test_index_detect_changes():
    """ Load file information from the file system and identify which notes need to be refreshed """
    assert False


def test_global_build_index(dual_folders):
    provider, index_builder = dual_folders

    directory = {
        "home": {"path": "/home"},
        "alpha": {"path": "/alpha"}
    }

    master = GlobalIndices(index_builder, directory=directory)
    master.load_all()



