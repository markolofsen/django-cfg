"""
Django CFG CLI Main Entry Point

Provides command-line interface for django-cfg operations.
"""

import click

from .commands.create_project import create_project
from .commands.info import info
from .commands.search import search


def get_version() -> str:
    """Get package version."""
    try:
        from importlib.metadata import version
        return version("django-cfg")
    except:
        return "1.0.0"


@click.group(name="django-cfg")
@click.version_option(version=get_version(), prog_name="django-cfg")
@click.help_option("--help", "-h")
def cli():
    """
    🚀 Django CFG - Production-ready Django configuration framework

    A simple CLI for creating Django projects from the latest template.
    """
    pass


# Register commands
cli.add_command(create_project)
cli.add_command(info)
cli.add_command(search)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
