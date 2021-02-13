"""
    Testing of the various classes and methods for loading, saving, parsing, and handling the markdown notes.
"""
import dateutil
import pytest
import tests.tools.sample_data as sample
from tests.tools.file_system_mocks import TestFileSystemProvider
from datetime import datetime as DateTime
from mnotes.notes.markdown_notes import NoteBuilder, MetaData, FailedMetadataException, _extract_yaml_front_matter, \
    NoteInfo
from dateutil import tz


# NoteBuilder class
# ======================================
# Conditions to test:
#   1. Missing metadata
#   2. No metadata end token (---)
#   3. Corrupted YAML
#   4. Broken creation timestamp
#   5. Ok


@pytest.fixture
def mock_builder():
    internal = {
        "/missing_metadata.md": {"content": sample.MD_MISSING_METADATA, "modified": 100},
        "/no_end_token.md": {"content": sample.MD_MISSING_END_TOKEN, "modified": 100},
        "/corrupted.md": {"content": sample.MD_CORRUPTED_YAML, "modified": 100},
        "/broken_timestamp.md": {"content": sample.MD_BROKEN_TIMESTAMP, "modified": 100},
        "/broken_timestamp2.md": {"content": sample.MD_BROKEN_TIMESTAMP_2, "modified": 100},
        "/ok.md": {"content": sample.MD_SAMPLE_NOTE_0, "modified": 100},
        "/extra.md": {"content": sample.MD_EXTRA_METADATA, "modified": 100},
    }
    provider = TestFileSystemProvider(internal)
    local = tz.gettz("America/New_York")
    return NoteBuilder(provider, local)


def test_missing_metadata(mock_builder):
    info = mock_builder.load_info("/missing_metadata.md")
    assert info.state == MetaData.MISSING


def test_no_end_token(mock_builder):
    info = mock_builder.load_info("/no_end_token.md")
    assert info.state == MetaData.FAILED


def test_corrupted_yaml(mock_builder):
    info = mock_builder.load_info("/corrupted.md")
    assert info.state == MetaData.FAILED


def test_broken_timestamp(mock_builder):
    info = mock_builder.load_info("/broken_timestamp.md")
    assert info.state == MetaData.FAILED


def test_broken_timestamp_2(mock_builder):
    info = mock_builder.load_info("/broken_timestamp2.md")
    assert info.state == MetaData.FAILED


def test_metadata_ok(mock_builder):
    info = mock_builder.load_info("/ok.md")
    assert info.state == MetaData.UNKNOWN


def test_load_note_missing(mock_builder):
    note = mock_builder.load_note("/missing_metadata.md")
    assert note.info.state == MetaData.MISSING
    assert note.content == sample.MD_MISSING_METADATA


def test_load_note_failed(mock_builder):
    note = mock_builder.load_note("/corrupted.md")
    assert note.info.state == MetaData.FAILED


def test_note_to_content_round_trip_works(mock_builder):
    note = mock_builder.load_note("/ok.md")
    text = note.to_file_text()
    _, meta, loaded_content = _extract_yaml_front_matter(text)
    meta["file_path"] = "/ok.md"

    assert note.info.to_dict() == NoteInfo(**meta).to_dict()
    assert loaded_content == note.content


def test_note_to_content_preserves_extra_keys(mock_builder):
    note = mock_builder.load_note("/extra.md")
    note.info.author = "New Author"
    file_content = note.to_file_text()

    state, meta, _ = _extract_yaml_front_matter(file_content)
    assert meta["author"] == "New Author"
    assert meta["source"] == "IPhone 19"
    assert sorted(meta["tags"]) == sorted(["synergy", "upcycle"])


def test_note_to_content_exception_on_failed_meta(mock_builder):
    note = mock_builder.load_note("/corrupted.md")
    with pytest.raises(FailedMetadataException):
        note.to_file_text()


def test_note_to_content_allows_missing_meta(mock_builder):
    note = mock_builder.load_note("/missing_metadata.md")
    note.info.author = "New Author"
    file_content = note.to_file_text()

    state, meta, _ = _extract_yaml_front_matter(file_content)
    assert {"author": "New Author", "created": None, "id": None, "title": None} == meta


def test_note_to_content_updates_id(mock_builder):
    note = mock_builder.load_note("/ok.md")
    note.info.id = "new-id"
    _, meta, _ = _extract_yaml_front_matter(note.to_file_text())

    assert "new-id" == meta['id']


def test_note_to_content_updates_title(mock_builder):
    note = mock_builder.load_note("/ok.md")
    note.info.title = "New Title"
    _, meta, _ = _extract_yaml_front_matter(note.to_file_text())

    assert "New Title" == meta['title']


def test_note_to_content_updates_author(mock_builder):
    note = mock_builder.load_note("/ok.md")
    note.info.author = "Author Person"
    _, meta, _ = _extract_yaml_front_matter(note.to_file_text())

    assert "Author Person" == meta['author']


def test_note_to_content_updates_created(mock_builder):
    d = DateTime(2020, 2, 2, 22, 0, 20, tzinfo=dateutil.tz.gettz("America/Los_Angeles"))
    note = mock_builder.load_note("/ok.md")
    note.info.created = d
    _, meta, _ = _extract_yaml_front_matter(note.to_file_text())

    assert d == meta['created']
