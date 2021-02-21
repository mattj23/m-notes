"""
    Tool for importing markdown and their metadata
"""
import os
import re
import yaml

from io import StringIO
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Set, Any, Union
from datetime import datetime as DateTime
from datetime import tzinfo

from ..utility.file_system import FileSystemProvider

ID_TIME_FORMAT = "%Y%m%d%H%M%S"
ID_LINK_PATTERN = re.compile(r"\[\[[^\]\[\n]*(\d{14})[^\]\[\n]*\]\]")


class FailedMetadataException(Exception):
    """ This operation cannot be completed because the note contains front matter which failed to parse. """
    pass


class MetaData(Enum):
    UNKNOWN = 0  # Initial, unknown state
    MISSING = 1  # The note was missing metadata completely
    FAILED = 2  # The metadata is presumably there but could not be parsed
    NO_ID = 3  # The metadata is missing an ID
    CONFLICT = 4  # The metadata has an ID conflict
    OK = 5  # The metadata has a validated unique ID


@dataclass
class NoteInfo:
    file_path: str
    created: Optional[DateTime]
    id: Optional[str]
    title: Optional[str]
    author: Optional[str]
    state: MetaData = MetaData.UNKNOWN
    info: Optional[str] = None
    links_to: Optional[List[str]] = None
    backlink: Optional[bool] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def rel_path(self, path: str) -> str:
        """ Display the path of this note relative to a given path """
        return os.path.relpath(self.file_path, start=path)

    @property
    def file_name(self):
        _, name = os.path.split(self.file_path)
        return name


class Note:
    def __init__(self, **kwargs):
        self.info: Optional[NoteInfo] = kwargs.get("info", None)
        self.front_matter: Optional[Dict] = kwargs.get("front_matter", None)
        self.content: Optional[str] = kwargs.get("content", None)

    def to_file_text(self) -> str:
        """
        Build the textual content of a file which would contain this note, re-serializing the front matter in YAML and
        inserting it on top of the content string.
        :return: The full text of the markdown note, front-matter included
        """
        assert isinstance(self.info, NoteInfo)

        if self.info.state == MetaData.FAILED:
            raise FailedMetadataException("It's unsafe to rebuild this note because it potentially contains front "
                                          "matter which simply failed to parse.")

        assert isinstance(self.front_matter, Dict)

        # Copy certain keys from the NodeInfo object to the dictionary about to be written
        info_dict = self.info.to_dict()
        for key in ("id", "title", "author", "created"):
            self.front_matter[key] = info_dict[key]

        if "backlink" in info_dict:
            self.front_matter["backlink"] = info_dict["backlink"]

        with StringIO() as writer:
            writer.write("---\n")
            yaml.dump(self.front_matter, writer)
            writer.write("---\n")
            writer.write(self.content)

            return writer.getvalue()


class NoteBuilder:
    """ Factory class to load and save the note information from a FileSystemProvider """

    def __init__(self, provider: FileSystemProvider, local_tz: tzinfo):
        self.local_zone = local_tz
        self.provider = provider

    def parse_date_time(self, value) -> Optional[DateTime]:
        """
        Create an optional datetime from one of the three possible values that the front matter might contain: a None,
        an ISO formatted representation, or an already parsed datetime. If the value is a string but cannot be parsed,
        a ValueError will be raised.
        """
        if value is None:
            return None

        if isinstance(value, str):
            return DateTime.fromisoformat(value).astimezone(self.local_zone)
        if isinstance(value, DateTime):
            return value

        raise ValueError(f"Could not decipher creation date from data: '{value}'")

    def _load_info_and_content(self, file_path: str) -> Tuple[NoteInfo, Optional[Dict], Optional[str]]:
        """
        Load a note's information and textual content from the file provider.
        :param file_path: must be a valid path to a file the provider can reach
        :return: a NoteInfo data object representing the results of the metadata parse operations
        """
        with self.provider.read_file(file_path) as handle:
            content = handle.read()

        state, meta_data, markdown_content = _extract_yaml_front_matter(content)

        # State can be either MISSING (no yaml front matter detected), FAILED (front matter was detected but was not
        # parseable), or UNKNOWN (it was loaded but we don't know the ID state yet)
        info_data = {"file_path": file_path, "state": state, "created": None, "id": None, "title": None, "author": None}

        if state == MetaData.FAILED:
            info_data["info"] = "Failed to parse YAML from document"
        elif state == MetaData.MISSING:
            info_data["info"] = "File missing metadata"
            meta_data = {}
        else:
            id_ = meta_data.get("id", None)
            if id_ is not None:
                id_ = str(id_)
            info_data.update({
                "id": id_,
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

        # Search for links
        links = ID_LINK_PATTERN.findall(markdown_content)
        if links:
            info_data["links_to"] = [e for e in links]

        return NoteInfo(**info_data), meta_data, markdown_content

    def load_info(self, file_path: str) -> NoteInfo:
        """
        Load a note and create a NoteInfo object from its contents. The NoteInfo.state field will be set based on the
        outcome of the operation, and can be MISSING, FAILED, or UNKNOWN. If one of the first two, the NoteInfo.info
        field will contain a message describing why the program believes that operation didn't complete.

        MISSING means no front-matter was detected, FAILED means we believe there is front matter but it's somehow
        malformed, not parse-able, or the creation date can't be parsed, and UNKNOWN means it loaded correctly but
        the validity of the contents can't be vouched for.

        :param file_path: must be a valid path to a file the provider can reach
        :return: a NoteInfo data object representing the results of the metadata parse operations
        """
        info, _, _ = self._load_info_and_content(file_path)
        return info

    def load_note(self, file_path: str) -> Note:
        """
        Load and create a Note object from a file path. The Note.info field will contain a standard NoteInfo object
        which will provide the state of the metadata loaded from the file.
        :param file_path: must be a valid path to a file the provider can reach
        :return: a Note data object containing both the contents of the metadata parse and the markdown content of the
        note itself
        """
        info, meta_data, markdown_content = self._load_info_and_content(file_path)
        return Note(info=info, front_matter=meta_data, content=markdown_content)


def _extract_yaml_front_matter(content: str) -> Tuple[MetaData, Optional[Dict], str]:
    """
    From a string containing the content of a markdown file that may or may not have front matter, this function will
    attempt to discover and deserialize YAML front matter into a python dictionary. This requires the file to start
    with either "---" or "...", contain a section of valid YAML, and then end with a line that is either "---" or "..."

    If it appears that there should be front matter but the information does not deserialize it will throw an error
    instead of returning None.

    Finally, if the note has two lines that look like this:

    ---
    # M-Note {..}

    ...everything underneath will be ignored.

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


def _strip_mnote_section(content: str) -> str:
    lines = content.split("\n")
    searchable = list(enumerate(line.strip() for line in lines))
    for i, line in searchable[:-1]:
        if line.startswith("---") and searchable[i+1][1].startswith("# M-Note"):
            return "\n".join(lines[:i]) + "\n"

    return content
