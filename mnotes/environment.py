import os
import click
import yaml
from typing import Optional


APPLICATION_NAME = "m-notes"
CONFIG_FILE = "m-notes.yaml"


class Config:
    def __init__(self, **kwargs):
        self.author: Optional[str] = kwargs.get("author", None)
        self.file: str = kwargs.get("file")

    def print(self):
        click.echo(click.style(f" * active config file: {self.file}", fg="blue"))
        click.echo(click.style(f" * default author: {self.author}", fg="blue"))

    def write(self):
        data = {
            "author": self.author,
        }
        with open(self.file, "w") as handle:
            yaml.dump(data, handle)


class MnoteEnvironment:
    def __init__(self):
        self.cwd = os.getcwd()
        self.config: Config = load_config()

    def print(self):
        click.echo(click.style(f" * current directory: {self.cwd}", fg="blue"))


pass_env = click.make_pass_decorator(MnoteEnvironment, ensure=True)


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


