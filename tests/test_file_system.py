from mnotes.utility.file_system import FileInfo


def test_file_info_path_join():
    info = FileInfo("/home/test/place", "my_note.md", 100, 10)
    assert info.full_path == "/home/test/place/my_note.md"


def test_file_info_to_dict():
    info = FileInfo("/home/test/place", "my_note.md", 100, 10)
    d = info.to_dict()

    expected = {'check_sum': None,
                'directory': '/home/test/place',
                'file_name': 'my_note.md',
                'last_modified': 100,
                'size': 10}

    assert d == expected


def test_file_info_from_dict():
    data = {'directory': '/home/test/place',
            'file_name': 'my_note.md',
            'last_modified': 100,
            'size': 10}
    info = FileInfo(**data)

    assert info.directory == "/home/test/place"
    assert info.file_name == "my_note.md"
    assert info.last_modified == 100
    assert info.size == 10
    assert info.check_sum is None
