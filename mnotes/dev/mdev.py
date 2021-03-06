"""
    M-Notes development tools
"""
from typing import List, Callable, Dict

import click
import pkg_resources
import random
from .sample_data_generator import (render_note, random_note, remove_author, remove_title, remove_created, remove_id,
                                    get_random_words, ALL_WORDS, conflicting_ids, add_link_to)

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
@click.option("--conflict", type=int, help="The number of samples with conflicting IDs to generate")
def sample(normal: int, author: int, created: int, ids: int, title: int, conflict: int):
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

    if conflict is not None:
        notes = conflicting_ids(conflict)
        save_notes(notes)


@main.command(name="linked")
@click.option("-n", type=int, required=True, help="Number of notes to generate")
@click.option("-l", type=int, required=True, help="Number of links to put in the corpus")
def linked(n: int, l: int):
    notes = [random_note() for i in range(n)]
    link_count = 0

    while link_count < l:
        target = random.choice(notes)
        source = random.choice(notes)
        if target["id"] == source['id']:
            continue

        add_link_to(source, target["id"])
        click.echo(f"Adding link to {target['id']} to note {source['id']}")
        link_count += 1

    save_notes(notes)


def save_notes(notes: List[Dict]):
    for note in notes:
        file_name_words = []
        for k in range(random.randint(5, 10)):
            file_name_words.append(random.choice(ALL_WORDS))
        file_name = " ".join(file_name_words)

        with open(f"{file_name}.md", "w") as handle:
            handle.write(render_note(note))


def gen_notes(count: int, apply: List[Callable]):
    notes = []
    for i in range(count):
        note = random_note()
        for c in apply:
            note = c(note)
        notes.append(note)

    save_notes(notes)
