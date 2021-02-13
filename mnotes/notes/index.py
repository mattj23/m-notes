import os
import json
from typing import List, Dict
from mnotes.utility.file_system import FileInfo, FileSystemProvider

from .markdown_notes import NoteMetadata

class NoteIndex:

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.path: str = kwargs.get("path")

        self.files: Dict[str, FileInfo] = {}
        self.notes: Dict[str, NoteMetadata] = {}

        for file_dict in kwargs.get("files", []):
            info = FileInfo(**file_dict)
            self.files[info.full_path] = info

        for note_dict in kwargs.get("notes", []):
            note = NoteMetadata(**note_dict)

    def serialize(self) -> str:
        output = {
            "name": self.name,
            "path": self.path,
            "files": [f.to_dict() for f in self.files.values()]
        }
        return json.dumps(output, indent=4)


class IndexBuilder:
    """ The IndexBuilder is a factory to build indices from a FileSystemProvider """

    def __init__(self, provider: FileSystemProvider):
        self.provider = provider

    def create(self, name: str, path: str) -> NoteIndex:
        index = NoteIndex(name=name, path=path)

        # Load all of the file information objects in the directory
        files = self.provider.get_all(path, lambda x: x.lower().endswith(".md"))
        for file_info in files:
            index.files[file_info.full_path] = file_info

        # Now we need to load all of the actual note metadata

        return index


class GlobalIndices:
    def __init__(self, provider: FileSystemProvider, **kwargs):
        self.provider = provider
        self.builder = IndexBuilder(self.provider)
        self.by_id = {}

        self.index_directory: Dict[str, Dict] = kwargs.get("directory", {})
        self.indices: Dict[str, NoteIndex] = {}

    def load_all(self):
        for name, info in self.index_directory.items():
            index = self.builder.create(name, info["path"])

            # The index must be merged in with the global set in order to detect
            # ID conflicts.

