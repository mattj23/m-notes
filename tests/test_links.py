from copy import deepcopy

import pytest

import tests.tools.sample_data as sample
from mnotes.notes.index import IndexBuilder, GlobalIndices
from mnotes.notes.markdown_notes import NoteBuilder
from tests.test_index import local_tz
from tests.tools.file_system_mocks import TestFileSystemProvider


@pytest.fixture
def link_index():
    provider = TestFileSystemProvider(deepcopy(sample.INDEX_WITH_LINKS))
    note_builder = NoteBuilder(provider, local_tz)
    index_builder = IndexBuilder(provider, note_builder)
    return provider, index_builder


def test_extracts_single_file_links_to(link_index):
    builder = link_index[1].note_builder
    note = builder.load_note("/links/note-01.md")

    assert sorted(note.info.links_to) == sorted(['20201204110546', '20160227182247'])


def test_links_generated(link_index):
    provider, builder = link_index
    index = builder.create("linked", "/")

    for note in index.notes.values():
        expected = sorted(sample.INDEX_WITH_LINKS_LINKS[note.id])
        assert expected == sorted(note.links_to)


def test_generate_backlinks(link_index):
    provider, builder = link_index
    master = GlobalIndices(builder, directory={"home": {"path": "/"}})
    master.load_all()

    backlinks = master.backlinks()

    assert sorted(backlinks["20160227182247"]) == sorted(["20031127103717", "19910802211642"])
