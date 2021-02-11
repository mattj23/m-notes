import os
import click
from mnotes.config import load_config, Config


class MnoteEnvironment:
    def __init__(self):
        self.cwd = os.getcwd()
        self.config: Config = load_config()

    def print(self):
        click.echo(click.style(f" * current working directory: {self.cwd}", fg="blue"))





