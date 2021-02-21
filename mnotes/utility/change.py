"""
    Abstraction of changes on the global set of notes
"""
from __future__ import annotations

import abc
from enum import Enum
from dataclasses import dataclass
from typing import Callable, List, Set, Tuple, Optional, Dict
from mnotes.notes.markdown_notes import NoteInfo, Note


class NoteChange:
    def __init__(self, note_info: NoteInfo, changer: NoteChanger, **kwargs):
        self.note_info = note_info
        self.new_file_path: Optional[str] = kwargs.get("file_path", None)
        self.new_id: Optional[str] = kwargs.get("new_id", None)

        self.change_data = kwargs.get("data", None)
        self.change_maker = changer

    def apply(self) -> Note:
        return self.change_maker.apply_change(self)


class ChangeTransaction:
    """
    The ChangeTransaction is an entirely in-memory representation of a set of changes to a global corpus of notes. It
    tracks the state of what has changed by its original filename.  All changes need to be checked against the
    transaction itself and not against the actual state on the filesystem, since changes set to occur before any
    specific change may alter the same note.
    """

    def __init__(self, ids: Set[str], paths: List[str], get_by_file: Callable[[str], Optional[Note]]):
        self.changes: List[NoteChange] = []
        self.getter = get_by_file

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

    def verify(self, change: NoteChange) -> bool:
        # Verify that the ID does not collide
        if change.new_id is not None:
            if change.new_id in self.ids:
                return False

        # Verify that the file path does not collide
        if change.new_file_path is not None and self._path_conflict(change.new_file_path):
            return False

        return True

    def get_note_state(self, original_path: str) -> Note:
        """
        Get the state of a note at this particular stage in the transaction. We'll refer to the note by the original
        filename before any renames occur.
        """
        if original_path not in self.by_path:
            raise KeyError(f"File {original_path} was not found as a known file in the index")

        if self.by_path[original_path] is None:
            # This is the first time we're touching this file in the transaction
            return self.getter(original_path)

        return self.by_path[original_path]

    def add_change(self, change: NoteChange):
        if not self.verify(change):
            raise ValueError("This change conflicts, make sure to use verify before trying to apply a change to a "
                             "transaction.")

        if change.new_id is not None:
            if change.note_info.id in self.ids:
                self.ids.remove(change.note_info.id)
            self.ids.add(change.new_id)

        if change.new_file_path is not None:
            self.file_moves[change.note_info.file_path] = change.new_file_path

        self.changes.append(change)
        self.by_path[change.note_info.file_path] = change.apply()

    def apply(self):
        pass


@dataclass
class TryChangeResult:
    class Result(Enum):
        NOTHING_TO_DO = 0
        FAILED = 1
        OK = 2

    result: Result
    change: Optional[NoteChange] = None
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
    def ok(change: NoteChange, message: Optional[List[List[str]]] = None) -> TryChangeResult:
        return TryChangeResult(TryChangeResult.Result.OK, change=change, message=message)

    @staticmethod
    def nothing(message: Optional[List[List[str]]] = None) -> TryChangeResult:
        return TryChangeResult(TryChangeResult.Result.NOTHING_TO_DO, message=message)


class NoteChanger(abc.ABC):
    """ Abstract base class encapsulating a thing that makes a change to a note in the context of the global
    index of all notes """

    def try_change(self, note_info: NoteInfo, transaction: ChangeTransaction) -> TryChangeResult:
        pass

    def apply_change(self, change: NoteChange) -> Note:
        pass
