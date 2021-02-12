import os
import shutil

import click
import yaml
from typing import Optional, Dict, Tuple, List

APPLICATION_NAME = "m-notes"
CONFIG_FILE = "m-notes.yaml"


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

    def print(self):
        click.echo(f" * active config file: {self.file}")
        click.echo(f" * default author: {self.author}")

    def write(self):
        data = {
            "author": self.author,
            "styles": self.styles.to_serializable()
        }
        if os.path.exists(self.file):
            shutil.copy(self.file, self.file + ".back")
        with open(self.file, "w") as handle:
            yaml.dump(data, handle)


class MnoteEnvironment:
    def __init__(self):
        self.cwd = os.getcwd()
        self.config: Config = load_config()

    def print(self):
        click.echo(f" * current directory: {self.cwd}")


pass_env = click.make_pass_decorator(MnoteEnvironment, ensure=True)


def echo_line(*args: str):
    for chunk in args[:-1]:
        click.echo(chunk, nl=False)
    click.echo(args[-1])


def load_config():
    config_root = click.get_app_dir(APPLICATION_NAME)
    config_file = os.path.join(config_root, CONFIG_FILE)

    if not os.path.exists(config_root):
        click.echo(click.style(f" * creating config directory {config_root}", fg="blue"))
        os.makedirs(config_root)

    if not os.path.exists(config_file):
        click.echo(click.style(f" * creating config file {config_file}", fg="blue"))

        default = {
            "author": None
        }

        with open(config_file, "w") as handle:
            yaml.dump(default, handle)

    with open(config_file, "r") as handle:
        config_dictionary = yaml.safe_load(handle)
    config_dictionary["file"] = config_file

    return Config(**config_dictionary)


