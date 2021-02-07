"""

"""
import os
import re
from datetime import datetime as DateTime
from typing import Tuple

long_stamp_pattern = re.compile(r"20\d{12}")
long_stamp_format = "%Y%m%d%H%M%S"


note_checks = {
    "created": {
        "description": "missing a creation time",
        "check": lambda x: x.created is None
    },
    "id": {
        "description": "missing an id",
        "check": lambda x: x.id is None
    },
    "id_filename": {
        "description": "missing an id in their filename",
        "check": lambda x: x.id is None or x.id not in x.file_name
    }
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


def to_timestamp_id(date_time: DateTime) -> str:
    return date_time.strftime(long_stamp_format)


def from_timestamp_id(time_stamp: str) -> DateTime:
    return DateTime.strptime(time_stamp, long_stamp_format)