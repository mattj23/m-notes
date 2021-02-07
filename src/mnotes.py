#!/usr/bin/python3
import os

import modes.summary as summary
import modes.fix_ids as fix_ids
import modes.fix_created as fix_created
import modes.fix_filename as fix_filename

import argparse

DEBUG_PATH = "evernote-data/patched"

parser = argparse.ArgumentParser()
command_group = parser.add_mutually_exclusive_group()
command_group.add_argument("--fix-created", nargs="?", const="", type=str,
                           help="fix the creation time on a specific filename, or all notes if blank")
command_group.add_argument("--fix-id", nargs="?", const="", type=str,
                           help="fix the id on a specific filename, or all notes if blank")
command_group.add_argument("--fix-name-id", nargs="?", const="", type=str,
                           help="put the id in a specific filename, or all notes if blank")

parser.add_argument("--summary-count", "-s", default=5, type=int, action="store",
                    help="number of results to display in summary mode")
parser.add_argument("--resolve", action="store_true", help="resolve conflicts during fix-id operation")

options = parser.parse_args()


def main():
    working_path = os.getcwd()
    working_path = DEBUG_PATH

    if options.fix_created is not None:
        fix_created.mode(working_path, options.fix_created)
        return
    elif options.fix_id is not None:
        fix_ids.mode(working_path, options.fix_id, options.resolve)
        return
    elif options.fix_name_id is not None:
        fix_filename.mode(working_path, options.fix_name_id)
        return

    # Summary mode
    summary.mode(working_path, options.summary_count)


if __name__ == '__main__':
    main()
