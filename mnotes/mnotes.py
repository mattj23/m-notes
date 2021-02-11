#
import os
import pkg_resources
import click
from typing import List, Optional

import mnotes.modes.fix_ids as fix_ids
import mnotes.modes.fix_created as fix_created
import mnotes.modes.fix_filename as fix_filename
import mnotes.modes.fix_title as fix_title

from mnotes.environment import MnoteEnvironment

mnote_version = pkg_resources.require("m-notes")[0].version


pass_env = click.make_pass_decorator(MnoteEnvironment, ensure=True)


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    click.echo()
    click.echo(click.style(f"M-Notes (v{mnote_version}) Markdown Note Manager", bold=True))

    # Load the environment
    ctx.obj = MnoteEnvironment()
    ctx.obj.print()

    if ctx.invoked_subcommand is None:
        pass
    else:
        pass
        # running the subcommand


@main.command()
@click.option("--author", type=str, help="Set default author")
@click.pass_context
@pass_env
def config(env: MnoteEnvironment, ctx, author: Optional[str]):
    env.config.print()

    if author:
        click.echo(click.style(f" * setting author to '{author}'", bold=True))
        env.config.author = author
        env.config.write()


@main.group(invoke_without_command=True)
@click.pass_context
@click.option("-n", default=5, show_default=True)
def fix(ctx, n: int):
    """
    Summarize the problems found in the corpus.
    /f
    :param ctx:
    :param n:
    :return:
    """
    if ctx.invoked_subcommand is None:
        # Summary mode
        summary.mode(os.getcwd(), n)


@fix.command()
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
def created(files: List[click.Path], n: Optional[int]):
    """
    Fix missing creation times from notes in the corpus.
    /f
    :param files:
    :param n:
    :return:
    """
    fix_created.mode(os.getcwd(), files, n)


@fix.command(name="id")
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--resolve", "resolve", flag_value=True,
              help="Attempt to resolve ID conflicts by adjusting creation time")
@click.argument("files", nargs=-1, type=click.Path())
def id_(files: List[click.Path], n: Optional[int], resolve: bool):
    """
    Generate IDs for notes in the corpus that are missing them. Use --resolve to reconcile potential ID
    mismatches by slightly adjusting the file creation time by a few seconds.
    /f
    :return:
    """
    fix_ids.mode(os.getcwd(), files, n, resolve)


@fix.command()
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.option("--complete", "complete", flag_value=True,
              help="Completely rewrite the filename from the title information")
@click.option("--force", "force", flag_value=True,
              help="Run the rename on all notes specified (use with --complete)")
@click.argument("files", nargs=-1, type=click.Path())
def filename(files: List[click.Path], n: Optional[int], complete: bool, force: bool):
    """
    Inserted IDs into filenames that are missing them, or use --complete to completely recreate
    filenames based on stripped and simplified versions of the note's *title* metadata.

    By default this will only run on files that do not have their ID in their filename. To do
    a complete rename on files which already have their ID, use the --force option
    /f
    :return:
    """
    fix_filename.mode(os.getcwd(), files, n, complete, force)


@fix.command()
@click.option("-n", default=None, type=int, help="Max number of fixes to perform")
@click.argument("files", nargs=-1, type=click.Path())
def title(files: List[click.Path], n: Optional[int]):
    """
    Fix missing titles in the note metadata by searching for leading H1 tag
    /f
    :return:
    """
    fix_title.mode(os.getcwd(), files, n)


