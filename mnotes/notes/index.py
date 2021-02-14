import os
import json
from typing import List, Dict
from datetime import tzinfo
from dataclasses import dataclass
from mnotes.utility.file_system import FileInfo, FileSystemProvider

from .markdown_notes import NoteInfo, NoteBuilder


@dataclass
class IndexOperationResult:
    note: FileInfo
    error: Exception


class NoteIndex:

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.path: str = kwargs.get("path")

        self.files: Dict[str, FileInfo] = {}
        self.notes: Dict[str, NoteInfo] = {}
        self.exceptions: List[IndexOperationResult] = []
        self.is_merged: bool = False    # Has this index been merged into the global index?

        for file_dict in kwargs.get("files", []):
            info = FileInfo(**file_dict)
            self.files[info.full_path] = info

        for note_dict in kwargs.get("notes", []):
            note = NoteInfo(**note_dict)

    def serialize(self) -> str:
        output = {
            "name": self.name,
            "path": self.path,
            "files": [f.to_dict() for f in self.files.values()],
            "notes": [n.to_dict() for n in self.notes.values()]
        }
        return json.dumps(output, indent=4)


class IndexBuilder:
    """ The IndexBuilder is a factory to build indices from a FileSystemProvider """

    def __init__(self, provider: FileSystemProvider, note_builder: NoteBuilder):
        self.provider = provider
        self.note_builder = note_builder

    def create(self, name: str, path: str) -> NoteIndex:
        index = NoteIndex(name=name, path=path)

        # Load all of the file information objects in the directory
        files = self.provider.get_all(path, lambda x: x.lower().endswith(".md"))
        for file_info in files:
            index.files[file_info.full_path] = file_info

        # Now we need to load all of the actual note metadata
        for file_path, file_info in index.files.items():
            try:
                index.notes[file_path] = self.note_builder.load_info(file_path)
            except Exception as e:
                index.exceptions.append(IndexOperationResult(file_info, e))

        return index


class GlobalIndices:
    def __init__(self, provider: FileSystemProvider, index_builder: IndexBuilder, **kwargs):
        self.provider = provider
        self.index_builder = index_builder
        self.by_id = {}

        self.index_directory: Dict[str, Dict] = kwargs.get("directory", {})
        self.indices: Dict[str, NoteIndex] = {}

    def load_all(self):
        for name, info in self.index_directory.items():
            index = self.index_builder.create(name, info["path"])

            # The index must be merged in with the global set in order to detect
            # ID conflicts.
