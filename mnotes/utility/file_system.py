"""
    Provides encapsulation of the filesystem to allow for testing.

"""

import abc
from datetime import datetime as DateTime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FileInfo:
    path: str
    file_name: str
    last_modified: DateTime
    check_sum: str


class FileSystemProvider(abc.ABC):

    def get_all(self) -> List[FileInfo]:
        pass
