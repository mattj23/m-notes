import pytest
from .file_system_mocks import TestFileSystemProvider, StringWrapper


@pytest.fixture
def mock_provider() -> TestFileSystemProvider:
    internal = {
        "/home/path/file1.md": {
            "content": "this is some content",
            "modified": 100
        },
        "/home/path/file2.md": {
            "content": "this is more content",
            "modified": 200
        },
        "/home/path/subpath/file.txt": {
            "content": "this is a text file",
            "modified": 300
        }
    }
    return TestFileSystemProvider(internal)


def test_string_wrapper():
    value = {"v": ""}

    def set_it(x):
        value["v"] = x

    with StringWrapper(set_it) as s:
        s.write("this is some test data")

    assert value["v"] == "this is some test data"


def test_mock_provider_get_all_base_path(mock_provider):
    info = mock_provider.get_all("/home/path")
    names = sorted(i.file_name for i in info)
    assert names == sorted(["file1.md", "file2.md", "file.txt"])


def test_mock_provider_get_all_short_path(mock_provider):
    info = mock_provider.get_all("/home/path/subpath")
    names = sorted(i.file_name for i in info)
    assert names == sorted(["file.txt"])


def test_mock_provider_get_all_markdown(mock_provider):
    info = mock_provider.get_all("/home/path", lambda s: s.lower().endswith(".md"))
    names = sorted(i.file_name for i in info)
    assert names == sorted(["file1.md", "file2.md"])


def test_mock_provider_read_works(mock_provider):
    with mock_provider.read_file("/home/path/file1.md") as handle:
        assert "this is some content" == handle.read()


def test_mock_provider_write_works(mock_provider):
    with mock_provider.write_file("/home/path/file2.md") as handle:
        handle.write("I replaced the content")

    assert "I replaced the content" == mock_provider.internal["/home/path/file2.md"]["content"]
