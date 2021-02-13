import os
from typing import TextIO, Optional, Callable, List, Dict

from mnotes.utility.file_system import FileSystemProvider, FileInfo


class TestFileSystemProvider(FileSystemProvider):

    def __init__(self, internal: Dict):
        self.internal = internal

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        pass

    def write_file(self, path) -> TextIO:
        pass

    def read_file(self, path) -> TextIO:
        pass
