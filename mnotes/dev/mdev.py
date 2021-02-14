"""
    M-Notes development tools
"""
from typing import List, Callable

import click
import pkg_resources
import random
from .sample_data_generator import (render_note, random_note, remove_author, remove_title, remove_created, remove_id,
                                    get_random_words, ALL_WORDS)

mnote_version = pkg_resources.require("m-notes")[0].version


@click.group()
@click.pass_context
def main(ctx: click.core.Context):
    pass


@main.command(name="sample")
@click.option("--normal", type=int, help="The number of normal sample notes to generate")
@click.option("--author", type=int, help="The number of samples with missing authors to generate")
@click.option("--created", type=int, help="The number of samples with missing creation times to generate")
@click.option("--ids", type=int, help="The number of samples with missing ids to generate")
@click.option("--title", type=int, help="The number of samples with missing titles to generate")
def sample(normal: int, author: int, created: int, ids: int, title: int):
    """ Generate sample data in the current folder """

    if normal is not None:
        gen_notes(normal, [])

    if author is not None:
        gen_notes(author, [remove_author])

    if created is not None:
        gen_notes(created, [remove_created, remove_id])

    if ids is not None:
        gen_notes(ids, [remove_id])

    if title is not None:
        gen_notes(title, [remove_title])


def gen_notes(count: int, apply: List[Callable]):
    for i in range(count):
        note = random_note()
        for c in apply:
            note = c(note)

        file_name_words = []
        for k in range(random.randint(5, 10)):
            file_name_words.append(random.choice(ALL_WORDS))
        file_name = " ".join(file_name_words)

        with open(f"{file_name}.md", "w") as handle:
            handle.write(render_note(note))
