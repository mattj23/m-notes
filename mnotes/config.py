import click
from typing import List, Dict, Optional
from mnotes.environment import MnoteEnvironment, pass_env, Styles, Style

_all_colors = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "bright_black", "bright_red",
               "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan", "bright_white")


@click.group()
@click.pass_context
@pass_env
def config(env: MnoteEnvironment, ctx: click.core.Context):
    """ Display and set global configuration parameters """

    if ctx.invoked_subcommand is None:
        env.config.print()

    # if author:
    #     click.echo(click.style(f" * setting author to '{author}'", bold=True))
    #     env.config.author = author
    #     env.config.write()


@config.command(name="author")
@click.argument("author", type=str)
@pass_env
def author_name(env: MnoteEnvironment, author: str):
    print(f"Author: {author}")


@config.command(name="style")
@click.option("--colors", flag_value=True, help="Show the colors by name on your terminal")
@pass_env
def text_style(env: MnoteEnvironment, colors: bool):
    if colors:
        show_color_table()
        return

    click.echo()
    click.echo("Current style configurations are shown below. To display the color options in your terminal, run "
               "'mnote config style --colors' and adjust your styles based on the way it looks.")

    for name, description, style_ in env.config.styles.to_display_list():
        click.echo()
        click.echo("Style: ", nl=False)
        click.echo(click.style(f"{name}", bold=True))
        click.echo(f" * {description}")
        click.echo(" * ", nl=False)
        style_.echo("This is some text in this style")
        for t in style_.display_attributes():
            click.echo(f" * {t}")


def show_color_table():
    click.echo()
    click.echo(click.style("ANSI terminal colors will display differently on different terminals and displays. The " 
                           "following output will show you what the colors will look like in your terminal with your "
                           "current settings."))
    click.echo()

    longest = max(len(name) for name in _all_colors) + 2
    for name in _all_colors:
        click.echo(f" * {name.ljust(longest)} ", nl=False)
        click.echo(click.style(f"this is text in this color  ", fg=name), nl=False)
        click.echo(click.style(" this is background ", bg=name))


