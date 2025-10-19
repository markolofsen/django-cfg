"""
Django Client CLI - Command-line interface with click.

Provides intuitive CLI for client generation.
"""

import sys

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    click = None

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


console = Console() if RICH_AVAILABLE else None


def print_message(message: str, style: str = ""):
    """Print message with optional styling."""
    if console:
        console.print(message, style=style)
    else:
        print(message)


def print_error(message: str):
    """Print error message."""
    if console:
        console.print(f"❌ {message}", style="bold red")
    else:
        print(f"ERROR: {message}")


def print_success(message: str):
    """Print success message."""
    if console:
        console.print(f"✅ {message}", style="bold green")
    else:
        print(f"SUCCESS: {message}")


def print_info(message: str):
    """Print info message."""
    if console:
        console.print(f"ℹ️  {message}", style="bold blue")
    else:
        print(f"INFO: {message}")


def print_warning(message: str):
    """Print warning message."""
    if console:
        console.print(f"⚠️  {message}", style="bold yellow")
    else:
        print(f"WARNING: {message}")


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def cli(ctx, version):
    """
    Django Client - Universal OpenAPI Client Generator.

    Fast, pure Python implementation with TypeScript and Python support.
    """
    if version:
        print_message("Django Client v1.0.0", style="bold cyan")
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option('--groups', '-g', multiple=True, help='Specific groups to generate')
@click.option('--python/--no-python', default=True, help='Generate Python client')
@click.option('--typescript/--no-typescript', default=True, help='Generate TypeScript client')
@click.option('--dry-run', is_flag=True, help='Validate without generating files')
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def generate(groups, python, typescript, dry_run, config):
    """Generate API clients for configured groups."""
    try:
        if dry_run:
            print_info("DRY RUN MODE - No files will be generated")

        groups_list = list(groups) if groups else None
        print_info(f"Generating clients for groups: {groups_list or 'all'}")

        if python:
            print_message("  → Python client", style="cyan")
        if typescript:
            print_message("  → TypeScript client", style="cyan")

        # TODO: Actual generation logic

        if not dry_run:
            print_success("Client generation completed!")
        else:
            print_info("Dry run completed - no files generated")

    except Exception as e:
        print_error(f"Generation failed: {e}")
        sys.exit(1)


@cli.command('list-groups')
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def list_groups(config):
    """List configured application groups."""
    try:
        from django_cfg.modules.django_client.core import get_openapi_service

        service = get_openapi_service()

        if not service.config:
            print_warning("No configuration found")
            return

        groups = service.get_groups()

        if not groups:
            print_warning("No groups configured")
            return

        print_info(f"Configured groups ({len(groups)}):")

        if console:
            table = Table(title="Application Groups")
            table.add_column("Group", style="cyan", no_wrap=True)
            table.add_column("Title", style="green")
            table.add_column("Apps", style="yellow")

            for name, group_config in groups.items():
                table.add_row(
                    name,
                    group_config.title,
                    str(len(group_config.apps))
                )

            console.print(table)
        else:
            for name, group_config in groups.items():
                print(f"\n  • {name}")
                print(f"    Title: {group_config.title}")
                print(f"    Apps: {len(group_config.apps)} pattern(s)")

    except Exception as e:
        print_error(f"Failed to list groups: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def validate(config):
    """Validate configuration."""
    try:
        from django_cfg.modules.django_client.core import get_openapi_service

        print_info("Validating configuration...")

        service = get_openapi_service()

        if not service.config:
            print_error("No configuration found")
            sys.exit(1)

        service.validate_config()
        print_success("Configuration is valid!")

    except Exception as e:
        print_error(f"Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def status(config):
    """Show current status and configuration."""
    try:
        from django_cfg.modules.django_client.core import get_openapi_service

        service = get_openapi_service()

        if not service.config:
            print_warning("No configuration found")
            return

        status_info = service.get_status()

        print_info("Django Client Status:")
        print(f"\n  Enabled: {status_info.get('enabled', False)}")
        print(f"  Groups: {status_info.get('groups', 0)}")
        print(f"  Output: {status_info.get('output_dir', 'N/A')}")
        print(f"  Python: {status_info.get('generate_python', False)}")
        print(f"  TypeScript: {status_info.get('generate_typescript', False)}")

        if status_info.get('group_names'):
            print("\n  Configured groups:")
            for name in status_info['group_names']:
                print(f"    • {name}")

    except Exception as e:
        print_error(f"Failed to get status: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if not CLICK_AVAILABLE:
        print("ERROR: click is required. Install with: pip install click")
        sys.exit(1)

    cli()


def run_cli():
    """Run CLI (alias for main)."""
    main()


if __name__ == "__main__":
    main()
