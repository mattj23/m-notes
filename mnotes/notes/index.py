from __future__ import annotations

import json
import os
from typing import List, Dict, Set, Callable, Optional
from dataclasses import dataclass
from mnotes.utility.file_system import FileInfo, FileSystemProvider

from .markdown_notes import NoteInfo, NoteBuilder, MetaData, Note
from ..utility.change import ChangeTransaction
from ..utility.json_encoder import MNotesEncoder, MNotesDecoder


@dataclass
class IndexOperationResult:
    note: FileInfo
    error: Exception


@dataclass
class IndexConflict:
    id: str
    existing: List[NoteInfo]
    conflicting: List[NoteInfo]


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

    def notes_in_path(self, path: str) -> List[NoteInfo]:
        """ Search the NoteIndex for notes which are in or below a specific directory. """
        check_path = os.path.abspath(path)
        return [n for n in self.notes.values() if n.file_path.startswith(check_path)]

    def serialize(self) -> str:
        output = {
            "name": self.name,
            "path": self.path,
            "files": [f.to_dict() for f in self.files.values()],
            "notes": [n.to_dict() for n in self.notes.values()]
        }
        return json.dumps(output, indent=4, cls=MNotesEncoder)

    def load_working(self, path: str, files: List) -> List[NoteInfo]:
        """
        Get the notes inside the specified path. If `files` are set it will check which of those paths match with
        notes inside the index and the path
        """
        if not files:
            return self.notes_in_path(path)
        else:
            abs_paths = map(os.path.abspath, files)
            return [self.notes[f] for f in abs_paths if f in self.notes]

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
        self.by_id: Dict[str, NoteInfo] = {}
        self.all_ids: Set[str] = set()
        self.by_path: Dict[str, NoteInfo] = {}

        # The cached field is for indices which were deserialized, and simply need to be updated
        self.cached: Dict[str, NoteIndex] = kwargs.get("cached", {})

        self.index_directory: Dict[str, Dict] = kwargs.get("directory", {})
        self.indices: Dict[str, NoteIndex] = {}
        self.conflicts: Dict[str, List[NoteInfo]] = {}

        # Callback to run after loading has finished
        self.on_load: Callable[[GlobalIndices], None] = kwargs.get("on_load", None)

    def get_note_info(self, path: str) -> Optional[NoteInfo]:
        return self.by_path[path] if path in self.by_path else None

    def get_note(self, path: str) -> Optional[Note]:
        if path in self.by_path:
            return self.index_builder.note_builder.load_note(path)
        return None

    def create_empty_transaction(self) -> ChangeTransaction:
        file_paths = []
        for index in self.indices.values():
            file_paths += list(index.files.keys())

        empty = ChangeTransaction(self.all_ids, file_paths, self.get_note, self.get_note_info)
        return empty

    def apply_transaction(self, transaction: ChangeTransaction):
        for original, moved in transaction.file_moves.items():
            if original != moved:
                self.index_builder.provider.move_file(original, moved)

            if transaction.by_path[original] is not None:
                with self.index_builder.provider.write_file(moved) as handle:
                    handle.write(transaction.by_path[original].to_file_text())

    def find_conflicts(self, path: str) -> Dict[str, IndexConflict]:
        """ Detect conflicts between the existing global index and the contents of a new directory """
        # Make sure to detect conflicts both in the by_id dictionary *and* the conflicts dictionary
        check_index = self.index_builder.create("!", path)
        new_conflicts: Dict[str, IndexConflict] = {}

        valid_ids: Dict[str, NoteInfo] = {}
        for note in check_index.notes.values():
            if note.id is None:
                continue

            # Check against existing, valid IDs in the global index
            if note.id in self.by_id:
                if note.id in new_conflicts:
                    new_conflicts[note.id].conflicting.append(note)
                else:
                    new_conflicts[note.id] = IndexConflict(note.id, [self.by_id[note.id]], [note])

            # Check against conflicts that already exist in the global index
            elif note.id in self.conflicts:
                if note.id in new_conflicts:
                    new_conflicts[note.id].conflicting.append(note)
                else:
                    new_conflicts[note.id] = IndexConflict(note.id, self.conflicts[note.id], [note])

            # Check against conflicts that are entirely within the new directory itself
            elif note.id in valid_ids:
                if note.id in new_conflicts:
                    new_conflicts[note.id].conflicting.append(note)
                else:
                    new_conflicts[note.id] = IndexConflict(note.id, [], [note])

            else:
                valid_ids[note.id] = note

        # Now sweep over the valid_id's to check if the third case occurred at any point
        for k, v in new_conflicts.items():
            if k in valid_ids:
                v.conflicting.append(valid_ids[k])
                del valid_ids[k]

        return new_conflicts

    def has_id(self, check_id: str) -> bool:
        """ Check if the ID exists anywhere in the global index, including in the current conflicts """
        return check_id in self.by_id or check_id in self.conflicts

    def backlinks(self) -> Dict[str, List[str]]:
        """
        Generate all backlinks for the entire global index in a single pass through all note information objects,
        creating a dictionary of lists in which the key is the ID for each note and the list is a list of IDs that
        link to this note. Notes with conflicting IDs do not get backlinks generated for them
        """
        bk_links: Dict[str, List[str]] = {}
        for note in filter(lambda n: n.links_to is not None, self.by_id.values()):
            for fwd in note.links_to:
                if fwd not in bk_links:
                    bk_links[fwd] = [note.id]
                else:
                    bk_links[fwd].append(note.id)

        return bk_links

    def load_all(self, force_checksum: bool = False):
        """
        Load all indices globally. This will attempt to start from pre-loaded indices which only need to be
        updated, as the update operation is a lot less intense than the new creation operation.

        After the indices are loaded the unique ids will be merged and conflicts detected.
        :param force_checksum: force the use of checksum for the update operation
        """
        self.by_id.clear()
        self.all_ids.clear()
        self.conflicts.clear()
        self.by_path.clear()

        # Update all of the indices
        for name, info in self.index_directory.items():
            index = self.cached.get(name, None)
            if index is None:
                index = self.index_builder.create(name, info["path"])

            self.index_builder.update(index, force_checksum)

            self.indices[name] = index

            # Go through each note and detect any conflicts against the global ID registry, and if there are none add
            # the note to the unified id dictionary.  If there is a conflict we'll add this note to the conflict
            # dictionary, but we will not remove the conflicting note yet, as this would prevent further conflicts
            # from being detected. Instead we'll handle the original conflict after all of the indices have been
            # merged.
            for note in self.indices[name].notes.values():
                self.by_path[note.file_path] = note
                if note.id is not None:
                    self.all_ids.add(note.id)
                    if note.id in self.by_id:
                        if note.id not in self.conflicts:
                            self.conflicts[note.id] = []
                        self.conflicts[note.id].append(note)
                    else:
                        self.by_id[note.id] = note
                else:
                    note.state = MetaData.NO_ID

        # Now that we're done merging all indices we'll go through all of the conflicts and remove the original note
        # which was first merged into the global dictionary, since it was added based on the happenstance of what
        # order things occurred in, and is not actually privileged over the other notes.
        for id_, conflict_list in self.conflicts.items():
            conflict_list.append(self.by_id[id_])
            del self.by_id[id_]
            for note in conflict_list:
                note.state = MetaData.CONFLICT

        for id_, note in self.by_id.items():
            note.state = MetaData.OK

        if self.on_load is not None:
            self.on_load(self)
