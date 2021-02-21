"""
    Abstraction of changes on the global set of notes
"""
from __future__ import annotations

import abc
from enum import Enum
from dataclasses import dataclass
from typing import Callable, List, Set, Tuple, Optional
from mnotes.notes.markdown_notes import NoteInfo


class NoteChange:
    def __init__(self, note_info: NoteInfo, changer: NoteChanger, **kwargs):
        self.note_info = note_info
        self.new_file_path: Optional[str] = kwargs.get("file_path", None)
        self.new_id: Optional[str] = kwargs.get("new_id", None)

        self.change_data = kwargs.get("data", None)
        self.change_maker = changer


class ChangeTransaction:
    def __init__(self):
        self.changes: List[NoteChange] = []
        self.ids: Set[str] = set()
        self.file_paths: Set[str] = set()

    def verify(self, change: NoteChange) -> bool:
        # Verify that the ID does not collide
        if change.new_id is not None:
            if change.new_id in self.ids:
                return False

        # Verify that the file path does not collide
        if change.new_file_path is not None:
            if change.new_file_path in self.file_paths:
                return False

        return True

    def add_change(self, change: NoteChange):
        if not self.verify(change):
            raise ValueError("This change conflicts, make sure to use verify before trying to apply a change to a "
                             "transaction.")

        if change.new_id is not None:
            if change.note_info.id in self.ids:
                self.ids.remove(change.note_info.id)
            self.ids.add(change.new_id)

        if change.new_file_path is not None:
            if change.note_info.file_path in self.file_paths:
                self.file_paths.remove(change.note_info.file_path)
            self.file_paths.add(change.new_file_path)

        self.changes.append(change)


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

    def apply_change(self, change: NoteChange):
        pass
