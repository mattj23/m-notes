"""
    Testing of the various classes and methods for loading, saving, parsing, and handling the markdown notes.
"""
import pytest
import tests.tools.sample_data as sample
from tests.tools.file_system_mocks import TestFileSystemProvider
from mnotes.notes.markdown_notes import NoteBuilder, MetaData
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
        "/ok.md": {"content": sample.MD_SAMPLE_NOTE_0, "modified": 100},
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


def test_metadata_ok(mock_builder):
    info = mock_builder.load_info("/ok.md")
    assert info.state == MetaData.UNKNOWN


