"""
    Provides encapsulation of the filesystem to allow for testing.

"""

import os
import abc
from datetime import datetime as DateTime
from dataclasses import dataclass
from typing import List, Optional, Callable


@dataclass
class FileInfo:
    directory: str
    file_name: str
    last_modified: float
    size: int
    check_sum: Optional[str] = None


class FileSystemProvider(abc.ABC):

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        pass


def _always_true(x):
    return True


class FileSystem(FileSystemProvider):

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
