"""
Django CFG CLI Main Entry Point

Provides command-line interface for django-cfg operations.
"""

import click
from pathlib import Path
from typing import Optional

from .commands.create_project import create_project
from .commands.info import info
from .utils import get_package_info
from ..utils.version_check import check_python_version


@click.group(name="django-cfg")
@click.version_option(version=get_package_info()["version"], prog_name="django-cfg")
@click.help_option("--help", "-h")
def cli():
    """
    🚀 Django CFG - Production-ready Django configuration framework
    
    A powerful CLI for managing Django projects with type-safe configuration,
    smart automation, and modern developer experience.
    """
    # Check Python version before any operations
    check_python_version("django-cfg CLI")


# Register commands
cli.add_command(create_project)
cli.add_command(info)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
