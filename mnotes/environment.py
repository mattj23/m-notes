import os
import shutil

import click
import yaml
from dataclasses import dataclass
from dateutil.tz import tzlocal
from datetime import tzinfo
from typing import Optional, Dict, Tuple, List
from mnotes.notes.index import GlobalIndices, NoteIndex
from mnotes.notes.markdown_notes import NoteBuilder
from mnotes.utility.file_system import FileSystemProvider

APPLICATION_NAME = "m-notes"
CONFIG_FILE = "m-notes.yaml"
GLOBAL_INDEX_FILE = "global-indices.yaml"


class Style:
    def __init__(self, **kwargs):
        if kwargs is None:
            kwargs = {}

        self.fg: Optional[str] = kwargs.get("fg", None)
        self.bg: Optional[str] = kwargs.get("bg", None)
        self.bold: Optional[bool] = kwargs.get("bold", None)
        self.underline: Optional[bool] = kwargs.get("underline", None)
        self.blink: Optional[bool] = kwargs.get("blink", None)
        self.reverse: Optional[bool] = kwargs.get("reverse", None)

    def as_dict(self):
        return self.__dict__

    def __call__(self, text, **kwargs) -> str:
        d = dict(self.as_dict())
        d.update(kwargs)
        return click.style(text, **self.as_dict())

    def echo(self, text, nl=True):
        click.echo(self(text), nl=nl)

    def display_attributes(self) -> List[str]:
        return sorted(f"{k}={v}" for k, v in self.as_dict().items())


class Styles:
    def __init__(self, **kwargs):
        self.warning = Style(**kwargs.get("warning", dict(fg="yellow")))
        self.success = Style(**kwargs.get("success", dict(fg="green", bold=True)))
        self.fail = Style(**kwargs.get("fail", dict(fg="red", bold=True)))
        self.visible = Style(**kwargs.get("visible", dict(fg="bright_blue")))

        self.map = {
            "warning": self.warning,
            "fail": self.fail,
            "success": self.success,
            "visible": self.visible
        }

        self.packed = (self.warning, self.fail, self.success, self.visible)

    def to_display_list(self) -> List[Tuple[str, str, Style]]:
        return [
            ("warning", "Style for text that highlights problems or issues", self.warning),
            ("fail", "Style for text that shows when an operation has failed", self.fail),
            ("success", "Style for text that shows a success condition", self.success),
            ("visible", "Style for text that should be visible or highlighted in a way that draws attention to it, but"
                        " is not necessarily good or bad", self.visible),
        ]

    def to_serializable(self):
        return {k: v.as_dict() for k, v in self.map.items()}


class Config:
    def __init__(self, **kwargs):
        self.author: Optional[str] = kwargs.get("author", None)
        self.file: str = kwargs.get("file")

        style_config: Dict = kwargs.get("styles", {})
        self.styles = Styles(**style_config)
        self.clear_on_run: bool = kwargs.get("clear_on_run", False)

    def print(self):
        click.echo(f" * active config file: {self.file}")
        click.echo(f" * default author: {self.author}")
        click.echo(f" * clear terminal on run: {self.clear_on_run}")

    def write(self):
        data = {
            "author": self.author,
            "styles": self.styles.to_serializable(),
            "clear_on_run": self.clear_on_run
        }
        if os.path.exists(self.file):
            shutil.copy(self.file, self.file + ".back")
        with open(self.file, "w") as handle:
            yaml.dump(data, handle)


class MnoteEnvironment:
    def __init__(self, config: Config, global_index: GlobalIndices, note_builder: NoteBuilder,
                 provider: FileSystemProvider, local_tz: tzinfo):
        self.cwd = os.path.abspath(os.getcwd())
        self.config: Config = config
        self.global_index: GlobalIndices = global_index
        self.note_builder: NoteBuilder = note_builder
        self.provider: FileSystemProvider = provider
        self.local_tz: tzinfo = local_tz

    def print(self):
        click.echo(f" * current directory: {self.cwd}")

    @property
    def index_of_cwd(self) -> Optional[NoteIndex]:
        """ Look at the current working directory and determine what index we're inside """
        # TODO: can this be cached? it shouldn't change once the program starts
        return self.get_index_of_path(self.cwd)

    @property
    def indices_in_cwd(self) -> List[NoteIndex]:
        contained = []
        check_abs = os.path.abspath(self.cwd)
        for index in self.global_index.indices.values():
            if os.path.abspath(index.path).startswith(check_abs):
                contained.append(index)
        return contained

    def get_index_of_path(self, path: str) -> Optional[NoteIndex]:
        check_abs = os.path.abspath(path)
        for index in self.global_index.indices.values():
            if check_abs.startswith(os.path.abspath(index.path)):
                return index
        return None


pass_env = click.make_pass_decorator(MnoteEnvironment, ensure=True)


def echo_line(*args: str):
    if not args:
        click.echo()
        return

    for chunk in args[:-1]:
        click.echo(chunk, nl=False)
    click.echo(args[-1])


@dataclass
class GlobalIndexData:
    directory: Dict[str, Dict]
    cached_indices: Dict[str, NoteIndex]


def load_global_index_data() -> GlobalIndexData:
    config_root = click.get_app_dir(APPLICATION_NAME)
    global_index_file = os.path.join(config_root, GLOBAL_INDEX_FILE)

    if not os.path.exists(global_index_file):
        return GlobalIndexData(directory={}, cached_indices={})

    # TODO: add check for corrupted file here
    with open(global_index_file, "r") as handle:
        directory = yaml.safe_load(handle)

    cached = {}
    for name, info in directory.items():
        cache_file = os.path.join(config_root, f"index-{name}.cached.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as handle:
                cached[name] = NoteIndex.deserialize(handle.read())

    return GlobalIndexData(directory=directory, cached_indices=cached)


def save_global_index_data(master: GlobalIndices):
    config_root = click.get_app_dir(APPLICATION_NAME)
    global_index_file = os.path.join(config_root, GLOBAL_INDEX_FILE)

    if os.path.exists(global_index_file):
        shutil.copy(global_index_file, global_index_file + ".back")

    with open(global_index_file, "w") as handle:
        yaml.dump(master.index_directory, handle)

    for name, index in master.indices.items():
        cache_file = os.path.join(config_root, f"index-{name}.cached.json")
        with open(cache_file, "w") as handle:
            handle.write(index.serialize())


def load_config():
    config_root = click.get_app_dir(APPLICATION_NAME)
    config_file = os.path.join(config_root, CONFIG_FILE)

    # Enforce the presence of the configuration directory
    if not os.path.exists(config_root):
        click.echo(click.style(f" * creating config directory {config_root}", fg="blue"))
        os.makedirs(config_root)

    # Enforce the presence of the configuration file, creating it if it does not exist
    if not os.path.exists(config_file):
        click.echo(click.style(f" * creating config file {config_file}", fg="blue"))
        config = Config(file=config_file)
        config.write()

    # Load the configuration file
    with open(config_file, "r") as handle:
        try:
            config_dictionary = yaml.safe_load(handle)
        except:
            click.echo(click.style(f"The M-Notes configuration file {config_file} appears to be corrupted or can't be "
                                   f"parsed. Check the file or revert to a previously known good version.",
                                   bold=True, fg="bright_red"))
            raise
    config_dictionary["file"] = config_file

    return Config(**config_dictionary)
