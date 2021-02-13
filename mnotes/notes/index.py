import json
from typing import List
from mnotes.utility.file_system import FileInfo, FileSystemProvider


class NoteIndex:

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.path: str = kwargs.get("path")

        self.files: List[FileInfo] = []

        for file in kwargs.get("files", []):
            self.files.append(FileInfo(**file))

    def serialize(self) -> str:
        output = {
            "name": self.name,
            "path": self.path,
            "files": [f.__dict__ for f in self.files]
        }
        return json.dumps(output, indent=4)


class IndexBuilder:
    def __init__(self, provider: FileSystemProvider):
        self.provider = provider

    def create(self, name: str, path: str) -> NoteIndex:
        files = self.provider.get_all(path, lambda x: x.lower().endswith(".md"))
        index = NoteIndex(name=name, path=path)
        index.files = files

        return index
