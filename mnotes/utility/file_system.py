"""
    Provides encapsulation of the filesystem to allow for testing.

"""
from __future__ import annotations

import os
import abc
from dataclasses import dataclass, asdict
from typing import List, Optional, Callable, Dict, TextIO
import hashlib


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

    def has_changed_from(self, other: FileInfo, use_checksum: bool = False) -> bool:
        """
        Try to determine if this FileInfo object has changed from another FileInfo object with the same path, used to
        see if a file has likely changed since an earlier FileInfo object was captured from it.

        If `use_checksum` is true, it will perform the comparison on the checksums. Be aware that if either of the two
        checksums has **not** been calculated and is `None` the comparison will always result in `True` as a safety
        measure.  If `use_checksum` is `False`, the comparison will return `True` if *either* the file size or the last
        modified time has changed (like with rsync)
        :param other: the other
        :param use_checksum:
        :return:
        """
        if other.full_path != self.full_path:
            raise ValueError("Do not attempt a comparison between two FileInfo objects that don't have the same path!")

        if use_checksum:
            return self.check_sum != other.check_sum or self.check_sum is None or other.check_sum is None
        return self.last_modified != other.last_modified or self.size != other.size


class FileSystemProvider(abc.ABC):
    """ Abstract base class encapsulating all operations which interact with the file system. """

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        pass

    def read_file(self, path: str) -> TextIO:
        pass

    def write_file(self, path: str) -> TextIO:
        pass

    def checksum(self, path: str) -> str:
        pass


class FileSystem(FileSystemProvider):
    """ Concrete implementation of a cross-platform FileSystemProvider based on Python's os and shutil module. """

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        predicate = _always_true if predicate is None else predicate
        results = []
        for root, dirs, files in os.walk(path):
            for f in filter(predicate, files):
                file_path = os.path.abspath(os.path.join(root, f))
                directory, file_name = os.path.split(file_path)
                modified = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                results.append(FileInfo(directory, file_name, modified, size))

        return results

    def read_file(self, path: str) -> TextIO:
        return open(path, "r")

    def write_file(self, path: str) -> TextIO:
        return open(path, "w")

    def checksum(self, path: str) -> str:
        sha = hashlib.sha1()
        with open(path, "rb") as handle:
            while True:
                data = handle.read(65536)
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()
