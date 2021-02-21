"""

"""
import os
import re
from datetime import datetime as DateTime
from typing import Tuple



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


