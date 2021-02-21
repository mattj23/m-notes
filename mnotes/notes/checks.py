"""

"""
import os
import re
from datetime import datetime as DateTime
from typing import Tuple

long_stamp_pattern = re.compile(r"20\d{12}")


note_checks = {
    "created": {
        "description": "missing a creation time",
        "check": lambda x: x.created is None,
        "hint": "try the 'mnote fix created' command"
    },
    "id": {
        "description": "missing an id",
        "check": lambda x: x.id is None,
        "hint": "try the 'mnote fix id' command"
    },
    "filename": {
        "description": "missing an id in their filename",
        "check": lambda x: x.id is None or x.id not in x.file_name,
        "hint": "try the 'mnote fix filename' command"
    },
    "title": {
        "description": "missing the title in the metadata",
        "check": lambda x: x.title is None,
        "hint": "try the 'mnote fix title' command"
    },
    "author": {
        "description": "missing an author",
        "check": lambda x: x.author is None,
        "hint": "try the 'mnote fix author' command"
    },
}


def file_c_time(file_path: str) -> Tuple[DateTime, bool]:
    """
    Get the file creation time from the operating system. This will not return good results on Linux
    :param file_path:
    :return: a datetime and a bool indicating whether it was the creation time or modification time returned
    """
    f_stat = os.stat(file_path)
    try:
        c_time = DateTime.fromtimestamp(f_stat.st_birthtime)
        return c_time, True
    except AttributeError:
        c_time = DateTime.fromtimestamp(f_stat.st_mtime)
    return c_time, False
