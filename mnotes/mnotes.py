#
import os
from typing import List, Optional

import click

import mnotes.modes.summary as summary
import mnotes.modes.fix_ids as fix_ids
import mnotes.modes.fix_created as fix_created
import mnotes.modes.fix_filename as fix_filename


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        print("M-Notes Overview")
    else:
        pass
        # running the subcommand


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
@click.argument("files", nargs=-1, type=click.Path())
def filename(files: List[click.Path], n: Optional[int], complete: bool):
    """
    Inserted IDs into filenames that are missing them, or use --complete to completely recreate
    filenames based on stripped and simplified versions of the note's *title* metadata.
    /f
    :return:
    """
    fix_filename.mode(os.getcwd(), files, n, complete)



# @main.command()
# def fix():
#     print("running fix")


# import argparse
#
# parser = argparse.ArgumentParser()
# command_group = parser.add_mutually_exclusive_group()
# command_group.add_argument("--fix-created", nargs="?", const="", type=str,
#                            help="fix the creation time on a specific filename, or all notes if blank")
# command_group.add_argument("--fix-id", nargs="?", const="", type=str,
#                            help="fix the id on a specific filename, or all notes if blank")
# command_group.add_argument("--fix-name-id", nargs="?", const="", type=str,
#                            help="put the id in a specific filename, or all notes if blank")
#
# parser.add_argument("--summary-count", "-s", default=5, type=int, action="store",
#                     help="number of results to display in summary mode")
# parser.add_argument("--resolve", action="store_true", help="resolve conflicts during fix-id operation")
#
# options = parser.parse_args()
#
#
# def main():
#     working_path = os.getcwd()
#
#     if options.fix_created is not None:
#         fix_created.mode(working_path, options.fix_created)
#         return
#     elif options.fix_id is not None:
#         fix_ids.mode(working_path, options.fix_id, options.resolve)
#         return
#     elif options.fix_name_id is not None:
#         fix_filename.mode(working_path, options.fix_name_id)
#         return
#
#     # Summary mode
#     summary.mode(working_path, options.summary_count)
#
#
# if __name__ == '__main__':
#     main()
