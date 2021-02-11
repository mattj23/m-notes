"""
    Tool for importing markdown and their metadata
"""

import os
import yaml
import pytz

from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime as DateTime

local_time_zone = pytz.timezone("America/New_York")


class NoteMetadata:
    def __init__(self, file_path: str, store_content=False):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.raw: Optional[Dict] = None
        self.created: Optional[DateTime] = None
        self.id: Optional[str] = None
        self.title: Optional[str] = None
        self.author: Optional[str] = None

        with open(file_path, "r") as handle:
            content = handle.read()

        stripped = content.strip().replace("...", "---")

        # Attempt to extract YAML front matter from the note. If none can be found the result will be None and
        # we can exit the initialization
        self.raw, normal_content = _extract_yaml_front_matter(stripped)
        if store_content:
            self.content = normal_content

        if self.raw is None:
            self.raw = {
                "created": None,
                "title": None,
                "author": None,
            }
            return

        if "created" in self.raw:
            created = self.raw["created"]
            if isinstance(created, str):
                self.created = DateTime.fromisoformat(self.raw["created"]).astimezone(local_time_zone)
            elif isinstance(created, DateTime):
                self.created = created

        self.title = self.raw.get("title")
        self.id = self.raw.get("id")
        self.author = self.raw.get("author")

    def rel_path(self, start: str) -> str:
        return os.path.relpath(self.file_path, start=start)

    @property
    def has_metadata(self):
        return self.raw is not None

    def save_file(self):
        if not hasattr(self, "content"):
            raise AttributeError("This object was loaded without storing the content, we cannot save it back to disk")
        self.raw["created"] = self.created
        self.raw["id"] = self.id
        self.raw["title"] = self.title
        self.raw["author"] = self.author
        output = dict(self.raw)
        output["created"] = self.created.isoformat()

        with open(self.file_path, "w") as handle:
            handle.write("---\n")
            yaml.dump(self.raw, handle)
            handle.write("---\n")
            handle.write(self.content)


def load_all_notes(working_directory: str) -> List[NoteMetadata]:
    notes = []
    for root, dirs, files in os.walk(working_directory):
        for f in filter(lambda x: x.endswith(".md"), files):
            path = os.path.join(root, f)
            notes.append(NoteMetadata(path))

    return notes


def get_existing_ids(notes: List[NoteMetadata]) -> Set[str]:
    """
    Get a set of existing note IDs from a list of note metadata objects. Will throw a ValueError if there are
    duplicated identifiers.
    """
    id_set = set()
    id_list = [note.id for note in notes if note.id is not None]
    duplicates = []

    for note_id in id_list:
        if note_id in id_set:
            duplicates.append(note_id)
        else:
            id_set.add(note_id)

    if duplicates:
        raise ValueError(f"The following ids are duplicated: {', '.join(duplicates)}")

    return id_set


def _extract_yaml_front_matter(content: str) -> Tuple[Optional[Dict], str]:
    """
    From a string containing the content of a markdown file that may or may not have front matter, this function will
    attempt to discover and deserialize YAML front matter into a python dictionary. This requires the file to start
    with either "---" or "...", contain a section of valid YAML, and then end with a line that is either "---" or "..."

    If it appears that there should be front matter but the information does not deserialize it will throw an error
    instead of returning None.
    :param content: the text content of the file
    :return: either None or a parsed dictionary
    """
    valid_tokens = ["...", "---"]
    lines = content.strip().split("\n")
    if lines[0].strip() not in valid_tokens:
        return None, content

    front_matter_lines = []
    normal_lines = []
    is_complete = False
    for line in lines[1:]:
        if not is_complete and line.strip() in valid_tokens:
            is_complete = True
            continue

        if is_complete:
            normal_lines.append(line)
        else:
            front_matter_lines.append(line)

    # If we had the start of a front matter block but never ended it we return None
    if not is_complete:
        return None, content

    normal_content = "\n".join(normal_lines)

    try:
        parsed = yaml.safe_load("\n".join(front_matter_lines))
        return parsed, normal_content
    except:
        raise ValueError("Could not parse the extracted front matter")






