import click
from typing import List, Dict, Optional
from mnotes.environment import MnoteEnvironment, pass_env


@click.command()
@click.option("--author", type=str, help="Set default author")
@click.pass_context
@pass_env
def config(env: MnoteEnvironment, ctx, author: Optional[str]):
    """ Display and set global configuration parameters """
    env.config.print()

    if author:
        click.echo(click.style(f" * setting author to '{author}'", bold=True))
        env.config.author = author
        env.config.write()







