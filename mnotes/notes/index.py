from __future__ import annotations

import os
import json
from typing import List, Dict
from datetime import tzinfo
from dataclasses import dataclass
from mnotes.utility.file_system import FileInfo, FileSystemProvider

from .markdown_notes import NoteInfo, NoteBuilder
from ..utility.json_encoder import MNotesEncoder, MNotesDecoder


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
        self.exceptions: Dict[str, IndexOperationResult] = {}
        self.is_merged: bool = False  # Has this index been merged into the global index?

        for file_dict in kwargs.get("files", []):
            info = FileInfo(**file_dict)
            self.files[info.full_path] = info

        for note_dict in kwargs.get("notes", []):
            note = NoteInfo(**note_dict)
            self.notes[note.file_path] = note

    def serialize(self) -> str:
        output = {
            "name": self.name,
            "path": self.path,
            "files": [f.to_dict() for f in self.files.values()],
            "notes": [n.to_dict() for n in self.notes.values()]
        }
        return json.dumps(output, indent=4, cls=MNotesEncoder)

    @staticmethod
    def deserialize(encoded: str) -> NoteIndex:
        dict_data = json.loads(encoded, cls=MNotesDecoder)
        return NoteIndex(**dict_data)


class IndexBuilder:
    """ The IndexBuilder is a factory to build indices from a FileSystemProvider """

    def __init__(self, provider: FileSystemProvider, note_builder: NoteBuilder):
        self.provider = provider
        self.note_builder = note_builder

    @staticmethod
    def _markdown_filter(s: str) -> bool:
        return s.lower().endswith(".md")

    def create(self, name: str, path: str) -> NoteIndex:
        index = NoteIndex(name=name, path=path)
        self.update(index, True)
        return index

    def update(self, index: NoteIndex, force_checksums: bool = False):
        """
        Update a NoteIndex by what's currently visible on the filesystem provider.  Performs the update in place.
        :param index: the NoteIndex object to perform the update on
        :param force_checksums: force the update to recalculate checksums for all of the files vs using modified
        timestamp and size
        """
        raw_witnessed: List[FileInfo] = self.provider.get_all(index.path, self._markdown_filter)
        witnessed: Dict[str, FileInfo] = {w.full_path: w for w in raw_witnessed}

        if force_checksums:
            for w in witnessed.values():
                w.check_sum = self.provider.checksum(w.full_path)

        # Determine items in the index that are no longer present in the witnessed information
        to_remove = []
        for k in index.files.keys():
            if k not in witnessed:
                to_remove.append(k)

        for k in to_remove:
            del index.files[k]
            del index.notes[k]
            if k in index.exceptions:
                del index.exceptions[k]

        # Add new witnessed items to the index, loading the notes from the file system
        for w in witnessed.values():
            key = w.full_path
            # Really relying on lazy evaluation here...
            if key not in index.files or w.has_changed_from(index.files[key], force_checksums):
                if key in index.exceptions:
                    del index.exceptions[key]

                index.files[key] = w
                try:
                    index.files[key].check_sum = self.provider.checksum(key)
                    index.notes[key] = self.note_builder.load_info(key)
                except Exception as e:
                    index.exceptions[key] = IndexOperationResult(w, e)


class GlobalIndices:
    """ The GlobalIndices is the master object for managing the entire collection of indices on the machine. The
    principle configuration is the *directory* dictionary, which is of the following structure:

        {
            "<index name 0>": { "path": "/home/user/Documents/index0" },
            "<index name 1>": { "path": /home/user/other_folder" },
            ...
        }
    """

    def __init__(self, index_builder: IndexBuilder, **kwargs):
        self.index_builder = index_builder
        self.by_id = {}

        self.index_directory: Dict[str, Dict] = kwargs.get("directory", {})
        self.indices: Dict[str, NoteIndex] = {}

    def load_all(self):
        for name, info in self.index_directory.items():
            index = self.index_builder.create(name, info["path"])

            # The index must be merged in with the global set in order to detect ID conflicts.
