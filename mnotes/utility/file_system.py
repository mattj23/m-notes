"""
    Provides encapsulation of the filesystem to allow for testing.

"""

import os
import abc
from dataclasses import dataclass, asdict
from typing import List, Optional, Callable, Dict, TextIO


def _always_true(x):
    return True


@dataclass
class FileInfo:
    directory: str
    file_name: str
    last_modified: float
    size: int
    check_sum: Optional[str] = None

    @property
    def full_path(self) -> str:
        return os.path.join(self.directory, self.file_name)

    def to_dict(self) -> Dict:
        return asdict(self)


class FileSystemProvider(abc.ABC):
    """ Abstract base class encapsulating all operations which interact with the file system. """

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        pass

    def read_file(self, path) -> TextIO:
        pass

    def write_file(self, path) -> TextIO:
        pass


class FileSystem(FileSystemProvider):
    """ Concrete implementation of a cross-platform FileSystemProvider based on Python's os and shutil module. """

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        predicate = _always_true if predicate is None else predicate
        results = []
        for root, dirs, files in os.walk(path):
            for f in filter(predicate, files):
                file_path = os.path.join(root, f)
                directory, file_name = os.path.split(file_path)
                modified = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                results.append(FileInfo(directory, file_name, modified, size))

        return results

    def read_file(self, path) -> TextIO:
        return open(path, "r")

    def write_file(self, path) -> TextIO:
        return open(path, "w")
