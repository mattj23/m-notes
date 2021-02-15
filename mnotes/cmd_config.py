import click
from typing import List, Dict, Optional
from mnotes.environment import MnoteEnvironment, pass_env, echo_line

_all_colors = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "bright_black", "bright_red",
               "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan", "bright_white")


@click.group(invoke_without_command=True)
@click.pass_context
@pass_env
def config(env: MnoteEnvironment, ctx: click.core.Context):
    """ Display and set global configuration parameters """
    click.echo(" * configuration mode")

    if ctx.invoked_subcommand is None:
        env.config.print()


@config.command(name="author")
@click.argument("author", type=str, nargs=-1)
@pass_env
def author_name(env: MnoteEnvironment, author: List[str]):
    """ Set the default author which M-Notes uses when fixing blank authors """
    if not author:
        echo_line(" * current author is ", click.style(f"'{env.config.author}'", bold=True))
        return

    if len(author) > 1:
        echo_line(env.config.styles.warning(" * only one author is allowed, if there are spaces in the author's name"
                                            " enclose the name with quotes"))
        return

    env.config.author = author[0].strip()
    env.config.write()
    echo_line()
    echo_line("Setting author to ", env.config.styles.visible(f"'{env.config.author}'", bold=True))


@config.command(name="clear")
@click.argument("on_off", type=click.Choice(["on", "off"], case_sensitive=False))
@pass_env
def clear_terminal(env: MnoteEnvironment, on_off: click.Choice):
    """ Set the option to clear the terminal whenever M-Notes is run """
    style = env.config.styles
    env.config.clear_on_run = on_off == "on"
    env.config.write()

    echo_line()
    if env.config.clear_on_run:
        echo_line("Clear terminal on run was turned ", style.success("ON"))
    else:
        echo_line("Clear terminal on run was turned ", style.fail("OFF"))


@config.command(name="style")
@click.option("--colors", flag_value=True, help="Show the colors by name on your terminal")
@click.option("--fg", type=str, default=None, help="Set the foreground color")
@click.option("--bg", type=str, default=None, help="Set the background color")
@click.option("--bold", type=bool, default=None, help="Set the text to be bold")
@click.option("--underline", type=bool, default=None, help="Set the text to be underlined")
@click.option("--blink", type=bool, default=None, help="Set the text to blink")
@click.option("--reverse", type=bool, default=None, help="Reverse the foreground and background")
@click.argument("style_name", type=str, nargs=-1)
@pass_env
def text_style(env: MnoteEnvironment, colors: bool, style_name: List[str], fg: Optional[str], bg: Optional[str],
               bold: Optional[bool], underline: Optional[bool], blink: Optional[bool], reverse: Optional[bool]):
    """
    View or set the colors and formatting for the different text styles used by M-Notes
    """
    if colors:
        click.echo(" * showing color table")
        show_color_table()
        return

    if style_name:
        click.echo(f" * styles provided: {', '.join(style_name)}")
        for name in style_name:
            if name not in env.config.styles.map:
                env.config.styles.fail.echo(f" * error: style name '{name}' is not a known M-Notes style")
                return

    for name in style_name:
        if fg is not None:
            if validate_color(noneify_color(fg)):
                env.config.styles.map[name].fg = noneify_color(fg)
            else:
                env.config.styles.fail.echo(f" * error: foreground color '{fg}' is not a valid color")

        if bg is not None:
            if validate_color(noneify_color(bg)):
                env.config.styles.map[name].bg = noneify_color(bg)
            else:
                env.config.styles.fail.echo(f" * error: background color '{bg}' is not a valid color")

        if bold is not None:
            env.config.styles.map[name].bold = bold

        if underline is not None:
            env.config.styles.map[name].underline = underline

        if blink is not None:
            env.config.styles.map[name].blink = blink

        if reverse is not None:
            env.config.styles.map[name].reverse = reverse

    env.config.write()

    click.echo()
    click.echo("Current style configurations are shown below. To display the color options in your terminal, run "
               "'mnote config style --colors' and adjust your styles based on the way it looks.")

    for name, description, style_ in env.config.styles.to_display_list():
        if style_name and name not in style_name:
            continue

        click.echo()
        click.echo(click.style("Style: ", underline=True), nl=False)
        click.echo(click.style(f"{name}", bold=True, underline=True))
        click.echo(f" * {description}")
        click.echo(" * ", nl=False)
        style_.echo(f"This is a sample of some text in the {name} style")
        click.echo(" * Attributes: ( " + ", ".join(style_.display_attributes()) + " )")


def validate_color(color_name: Optional[str]) -> bool:
    if color_name is None:
        return True
    return color_name in _all_colors


def noneify_color(color_name: str) -> Optional[str]:
    if color_name is not None and color_name.lower() == "none":
        return None
    return color_name


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
