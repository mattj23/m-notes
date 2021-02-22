"""
    Abstraction of changes on the global set of notes
"""
from __future__ import annotations

import abc
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from typing import Callable, List, Set, Tuple, Optional, Dict
from mnotes.notes.markdown_notes import NoteInfo, Note


class ChangeTransaction:
    """
    The ChangeTransaction is an entirely in-memory representation of a set of changes to a global corpus of notes. It
    tracks the state of what has changed by its original filename.  All changes need to be checked against the
    transaction itself and not against the actual state on the filesystem, since changes set to occur before any
    specific change may alter the same note.
    """

    def __init__(self, ids: Set[str], paths: List[str], get_note_by_file: Callable[[str], Optional[Note]],
                 get_note_info_by_file: Callable[[str], Optional[NoteInfo]]):
        self._get_note_from_index = get_note_by_file
        self._get_note_info_from_index = get_note_info_by_file

        # Note data mapped to the *original* file path that the note was at. If the note data is None, it means the
        # transaction doesn't affect this note
        self.by_path: Dict[str, Optional[Note]] = {}

        # Note new path mapped to the note *original* path. If the two are equal, the note is not being moved. Checking
        # for a conflict in the file names involves checking for a conflict against the *values*, not the keys
        self.file_moves: Dict[str, str] = {}

        # This needs to be set externally when this object is created
        self.ids: Set[str] = ids

        # Construct the by_path and file_moves dictionaries
        for path in paths:
            self.file_moves[path] = path
            self.by_path[path] = None

    def _path_conflict(self, path: str) -> bool:
        # TODO: this can probably be cached when updated
        return path in set(self.file_moves.values())

    def verify(self, original_path: str, update: Note) -> bool:
        original = self.get_note_info_state(original_path)

        # Verify that the ID does not collide
        if original.id != update.info.id:
            if update.info.id in self.ids:
                return False

        # Verify that the file path does not collide
        if (original.file_path != update.info.file_path) and self._path_conflict(update.info.file_path):
            return False

        return True

    def get_note_info_state(self, original_path: str) -> Optional[NoteInfo]:
        """ Get the note information """
        if original_path not in self.by_path:
            raise KeyError(f"File {original_path} was not found as a known file in the index")

        if self.by_path[original_path] is None:
            # This is the first time we're touching this file in the transaction
            return deepcopy(self._get_note_info_from_index(original_path))

        return deepcopy(self.by_path[original_path].info)

    def get_note_state(self, original_path: str) -> Optional[Note]:
        """
        Get the state of a note at this particular stage in the transaction. We'll refer to the note by the original
        filename before any renames occur.
        """
        if original_path not in self.by_path:
            raise KeyError(f"File {original_path} was not found as a known file in the index")

        if self.by_path[original_path] is None:
            # This is the first time we're touching this file in the transaction
            return deepcopy(self._get_note_from_index(original_path))

        return deepcopy(self.by_path[original_path])

    def add_change(self, original_path: str, update: Note):
        if not self.verify(original_path, update):
            raise ValueError("This change conflicts, make sure to use verify before trying to apply a change to a "
                             "transaction.")

        original = self.get_note_info_state(original_path)

        # Verify that the ID does not collide
        if original.id != update.info.id:
            if original.id in self.ids:
                self.ids.remove(original.id)
            self.ids.add(update.info.id)

        # Verify that the file path does not collide
        if original.file_path != update.info.file_path:
            self.file_moves[original_path] = update.info.file_path

        self.by_path[original_path] = update


@dataclass
class TryChangeResult:
    class Result(Enum):
        NOTHING_TO_DO = 0
        FAILED = 1
        OK = 2

    result: Result
    change: Optional[Note] = None
    message: Optional[List[List[str]]] = None

    @property
    def is_failed(self):
        return self.result == TryChangeResult.Result.FAILED

    @property
    def is_nothing(self):
        return self.result == TryChangeResult.Result.NOTHING_TO_DO

    @property
    def is_ok(self):
        return self.result == TryChangeResult.Result.OK

    @staticmethod
    def failed(message: Optional[List[List[str]]] = None) -> TryChangeResult:
        return TryChangeResult(TryChangeResult.Result.FAILED, message=message)

    @staticmethod
    def ok(updated: Note, message: Optional[List[List[str]]] = None) -> TryChangeResult:
        return TryChangeResult(TryChangeResult.Result.OK, change=updated, message=message)

    @staticmethod
    def nothing(message: Optional[List[List[str]]] = None) -> TryChangeResult:
        return TryChangeResult(TryChangeResult.Result.NOTHING_TO_DO, message=message)


class NoteChanger(abc.ABC):
    """ Abstract base class encapsulating a thing that makes a change to a note in the context of the global
    index of all notes """

    def try_change(self, original_path: str, transaction: ChangeTransaction) -> TryChangeResult:
        pass

