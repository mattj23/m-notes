import pytest
from copy import deepcopy
from dateutil import tz
import tests.tools.sample_data as sample
from tests.tools.file_system_mocks import TestFileSystemProvider

from mnotes.notes.markdown_notes import NoteBuilder
from mnotes.notes.index import IndexBuilder, NoteIndex


local_tz = tz.gettz("Africa/Harare")


def test_index_serialize_round_trip():
    provider = TestFileSystemProvider(deepcopy(sample.INDEX_FIVE_NORMAL_NOTES))
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)

    index = index_builder.create("test", "/")
    serialized = index.serialize()

    loaded = NoteIndex.deserialize(serialized)

    assert index.name == loaded.name
    assert index.path == loaded.path
    assert index.files == loaded.files
    assert index.notes == loaded.notes
