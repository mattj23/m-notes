"""
    Tool for importing markdown and their metadata
"""

import os
import yaml
import pytz

from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Set, Any, Union
from datetime import datetime as DateTime
from datetime import tzinfo

from ..utility.file_system import FileSystemProvider

local_time_zone: tzinfo = pytz.timezone("America/New_York")


class MetaData(Enum):
    UNKNOWN = 0     # Initial, unknown state
    MISSING = 1     # The note was missing metadata completely
    FAILED = 2      # The metadata is presumably there but could not be parsed
    NO_ID = 3       # The metadata is missing an ID
    CONFLICT = 4    # The metadata has an ID conflict
    OK = 5          # The metadata has a validated unique ID


@dataclass
class NoteInfo:
    file_path: str
    created: Optional[DateTime]
    id: Optional[str]
    title: Optional[str]
    author: Optional[str]
    state: MetaData = MetaData.UNKNOWN
    info: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class NoteMetadata:
    def __init__(self, file_path: str, store_content=False):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.raw: Optional[Dict] = None
        self.created: Optional[DateTime] = None
        self.id: Optional[str] = None
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.state: MetaData = MetaData.UNKNOWN

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


class NoteBuilder:
    """ Factory class to load and save the note information from a FileSystemProvider """

    def __init__(self, provider: FileSystemProvider, local_tz: tzinfo):
        self.local_zone = local_tz
        self.provider = provider

    def parse_date_time(self, value) -> Optional[DateTime]:
        if value is None:
            return None

        if isinstance(value, str):
            return DateTime.fromisoformat(value).astimezone(self.local_zone)
        if isinstance(value, DateTime):
            return value

        raise ValueError(f"Could not decipher creation date from data: '{value}'")

    def load_info(self, file_path: str) -> NoteInfo:
        with self.provider.read_file(file_path) as handle:
            content = handle.read()

        state, meta_data, markdown_content = _extract_yaml_front_matter(content)

        # State can be either MISSING (no yaml front matter detected), FAILED (front matter was detected but was not
        # parseable), or UNKNOWN (it was loaded but we don't know the ID state yet)
        info_data = { "file_path": file_path, "state": state }

        if state == MetaData.FAILED:
            info_data["info"] = "Failed to parse YAML from document"
        elif state == MetaData.MISSING:
            info_data["info"] = "File missing metadata"
        else:
            info_data.update({
                "id": meta_data.get("id", None),
                "title": meta_data.get("title", None),
                "author": meta_data.get("author", None),
            })

        # The parsing of the creation date is somewhat complicated and has the potential to fail
        try:
            info_data["created"] = self.parse_date_time(meta_data.get("created", None))
        except ValueError as e:
            info_data["created"] = None
            info_data["info"] = "Failed to parse creation time stamp"
            info_data["state"] = MetaData.FAILED

        return NoteInfo(**info_data)


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


def _extract_yaml_front_matter(content: str) -> Tuple[MetaData, Optional[Dict], str]:
    """
    From a string containing the content of a markdown file that may or may not have front matter, this function will
    attempt to discover and deserialize YAML front matter into a python dictionary. This requires the file to start
    with either "---" or "...", contain a section of valid YAML, and then end with a line that is either "---" or "..."

    If it appears that there should be front matter but the information does not deserialize it will throw an error
    instead of returning None.
    :param content: the text content of the file
    :return:
    """
    valid_tokens = ["...", "---"]
    lines = content.strip().split("\n")
    if lines[0].strip() not in valid_tokens:
        return MetaData.MISSING, None, content

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
        return MetaData.FAILED, None, content

    normal_content = "\n".join(normal_lines)

    try:
        parsed = yaml.safe_load("\n".join(front_matter_lines))
        return MetaData.UNKNOWN, parsed, normal_content
    except:
        return MetaData.FAILED, None, content




