"""
Django CFG Create Project Command

Creates a new Django project by downloading the solution template from GitHub.
"""

import logging
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import click
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from django_cfg.config import (
    LIB_SITE_URL,
    TEMPLATE_ARCHIVE_URL,
    TEMPLATE_PATH_IN_ARCHIVE,
)

logger = logging.getLogger(__name__)

# Download configuration
DOWNLOAD_TIMEOUT = 120  # seconds
USER_AGENT = "django-cfg/1.0"
MAX_RETRY_ATTEMPTS = 3
RETRY_MIN_WAIT = 2  # seconds
RETRY_MAX_WAIT = 10  # seconds


def _is_interactive() -> bool:
    """Check if running in interactive terminal."""
    return sys.stdout.isatty()


def _download_with_progress(
    response: requests.Response,
    temp_file,
    total_size: int,
) -> None:
    """Download with Rich progress bar if in interactive mode."""
    if _is_interactive() and total_size > 0:
        try:
            from rich.progress import (
                Progress,
                DownloadColumn,
                TransferSpeedColumn,
                BarColumn,
                TextColumn,
                TimeRemainingColumn,
            )

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    "[cyan]Downloading template...",
                    total=total_size
                )
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                    progress.update(task, advance=len(chunk))
        except ImportError:
            _download_simple(response, temp_file, total_size)
    else:
        _download_simple(response, temp_file, total_size)


def _download_simple(
    response: requests.Response,
    temp_file,
    total_size: int,
) -> None:
    """Simple download without progress bar (for CI/CD)."""
    downloaded = 0
    last_percent = 0

    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)
        downloaded += len(chunk)

        if total_size > 0:
            percent = int(downloaded * 100 / total_size)
            if percent >= last_percent + 10:
                last_percent = percent
                click.echo(f"   Downloaded {percent}%")


@retry(
    stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ChunkedEncodingError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _download_template() -> Path:
    """Download template archive from GitHub with retry logic."""
    click.echo("📥 Downloading template from GitHub...")
    click.echo(f"   URL: {TEMPLATE_ARCHIVE_URL}")

    temp_path = None

    try:
        response = requests.get(
            TEMPLATE_ARCHIVE_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=DOWNLOAD_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        total_size = int(content_length) if content_length else 0

        if total_size > 0:
            size_mb = total_size / (1024 * 1024)
            click.echo(f"   Size: {size_mb:.1f} MB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            temp_path = Path(temp_file.name)
            _download_with_progress(response, temp_file, total_size)

        click.echo("✅ Template downloaded successfully")
        return temp_path

    except requests.exceptions.HTTPError as e:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(f"HTTP error downloading template: {e}")
    except Exception as e:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise


def _extract_template(archive_path: Path, target_path: Path) -> int:
    """
    Extract template archive to target directory.

    Only extracts files from TEMPLATE_PATH_IN_ARCHIVE (solution/).

    Returns:
        Number of extracted files
    """
    click.echo("📂 Extracting template...")

    try:
        with zipfile.ZipFile(archive_path, 'r') as archive:
            members = archive.namelist()

            # Find the root folder name (django-cfg-main)
            root_folder = members[0].split('/')[0] if members else None

            if not root_folder:
                raise ValueError("Archive structure is invalid")

            # Path to solution directory: django-cfg-main/solution/
            template_prefix = f"{root_folder}/{TEMPLATE_PATH_IN_ARCHIVE}/"

            extracted_files = 0
            for member in members:
                # Skip if not in template path
                if not member.startswith(template_prefix):
                    continue

                # Calculate relative path (remove template_prefix)
                relative_path = member[len(template_prefix):]

                # Skip empty paths (directory markers)
                if not relative_path:
                    continue

                # Skip docker volumes directory
                if relative_path.startswith("docker/volumes/"):
                    continue

                # Target file path
                target_file = target_path / relative_path

                # Extract file
                if member.endswith('/'):
                    # Create directory
                    target_file.mkdir(parents=True, exist_ok=True)
                else:
                    # Create parent directories
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    # Extract file content
                    with archive.open(member) as source:
                        with open(target_file, 'wb') as target:
                            target.write(source.read())

                    extracted_files += 1

        click.echo(f"✅ Template extracted ({extracted_files} files)")
        return extracted_files

    except zipfile.BadZipFile:
        raise ValueError("Invalid template archive")
    except Exception as e:
        raise RuntimeError(f"Failed to extract template: {e}")


def _show_next_steps(target_path: Path, project_name: str) -> None:
    """Show beautiful next steps guide using Rich."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich.syntax import Syntax
        from rich import box

        console = Console()
        django_rel = "projects/django"

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[bold green]✅ Project '{project_name}' created successfully![/bold green]",
            border_style="green"
        ))

        # Project structure
        structure = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        structure.add_column("", style="dim")
        structure.add_row(f"📁 {project_name}/")
        structure.add_row("   ├── docker/              [dim]# Docker deployment[/dim]")
        structure.add_row("   ├── docs/                [dim]# Setup guides (README)[/dim]")
        structure.add_row("   └── projects/")
        structure.add_row("       ├── django/          [dim]# Django backend[/dim]")
        structure.add_row("       ├── frontend/        [dim]# Next.js frontend[/dim]")
        structure.add_row("       └── electron/        [dim]# Desktop app[/dim]")
        console.print(structure)

        # Configuration files panel
        config_files = Table(show_header=True, header_style="bold yellow", box=box.ROUNDED)
        config_files.add_column("File", style="cyan", width=35)
        config_files.add_column("Description", style="white")

        config_files.add_row(f"{django_rel}/api/environment/.env", "Environment variables (DATABASE_URL, secrets)")
        config_files.add_row(f"{django_rel}/api/environment/.env.prod", "Production overrides")
        config_files.add_row(f"{django_rel}/api/environment/loader.py", "Pydantic settings loader")
        config_files.add_row(f"{django_rel}/api/config.py", "Django-CFG configuration class")

        console.print()
        console.print(Panel(config_files, title="[bold]⚙️ Configuration Files[/bold]", border_style="yellow"))

        # Next steps panel
        steps = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        steps.add_column("#", style="bold", width=3)
        steps.add_column("Action", style="white")
        steps.add_column("Command / File", style="green")

        steps.add_row("1", "Navigate to Django", f"cd {project_name}/{django_rel}")
        steps.add_row("2", "Edit environment", "nano api/environment/.env")
        steps.add_row("", "[dim]Set DATABASE__URL, SECRET_KEY[/dim]", "")
        steps.add_row("3", "Install dependencies", "poetry install")
        steps.add_row("4", "Run migrations", "poetry run python manage.py migrate")
        steps.add_row("5", "Create superuser", "poetry run python manage.py superuser")
        steps.add_row("6", "Start server", "poetry run python manage.py runserver")

        console.print()
        console.print(Panel(steps, title="[bold]📋 Next Steps[/bold]", border_style="blue"))

        # Quick start commands
        console.print()
        console.print("[bold yellow]⚡ Quick Start:[/bold yellow]")
        console.print(f"[dim]$[/dim] cd {project_name}/{django_rel}")
        console.print("[dim]$[/dim] nano api/environment/.env  [italic]# Set DATABASE__URL[/italic]")
        console.print("[dim]$[/dim] poetry install")
        console.print("[dim]$[/dim] poetry run python manage.py migrate")
        console.print("[dim]$[/dim] poetry run python manage.py superuser")
        console.print("[dim]$[/dim] poetry run python manage.py runserver")

        # Docker option
        console.print()
        console.print("[bold yellow]🐳 Docker Deployment:[/bold yellow]")
        console.print(f"[dim]$[/dim] cd {project_name}/docker")
        console.print("[dim]$[/dim] docker-compose -f docker-compose-local.yaml up -d")

        # AI Documentation
        console.print()
        console.print("[bold yellow]🤖 AI Documentation (MCP Server):[/bold yellow]")
        console.print("[dim]Add to Claude/Cursor config:[/dim]")
        console.print('[cyan]{"mcpServers": {"djangocfg": {"url": "https://mcp.djangocfg.com/mcp"}}}[/cyan]')

        # Features
        features = Table(show_header=False, box=None, padding=(0, 1))
        features.add_column("", width=30)
        features.add_column("", width=30)
        features.add_row("🤖 AI-native docs (MCP)", "🔧 Pydantic v2 config")
        features.add_row("🎨 Unfold admin UI", "📊 API documentation")
        features.add_row("🔐 JWT authentication", "🗃️ Multi-database")
        features.add_row("⚡ Django-RQ tasks", "🐳 Docker ready")

        console.print()
        console.print(Panel(features, title="[bold]💡 Features Included[/bold]", border_style="magenta"))

        # Documentation links
        console.print()
        console.print("[bold]📚 Documentation:[/bold]")
        console.print(f"   [link={LIB_SITE_URL}]{LIB_SITE_URL}[/link]")
        console.print(f"   [dim]{project_name}/docs/[/dim] - Local setup guides")
        console.print()

    except ImportError:
        # Fallback to plain output if Rich not available
        _show_next_steps_plain(target_path, project_name)


def _show_next_steps_plain(target_path: Path, project_name: str) -> None:
    """Fallback plain text output if Rich is not available."""
    django_rel = "projects/django"

    click.echo()
    click.echo(f"✅ Project '{project_name}' created successfully!")
    click.echo(f"📁 Location: {target_path}")
    click.echo()
    click.echo("⚙️ Configuration Files:")
    click.echo(f"   {django_rel}/api/environment/.env      - Environment variables")
    click.echo(f"   {django_rel}/api/environment/.env.prod - Production overrides")
    click.echo(f"   {django_rel}/api/environment/loader.py - Pydantic settings loader")
    click.echo(f"   {django_rel}/api/config.py             - Django-CFG configuration")
    click.echo()
    click.echo("📋 Next Steps:")
    click.echo(f"   1. cd {project_name}/{django_rel}")
    click.echo("   2. nano api/environment/.env  # Set DATABASE__URL, SECRET_KEY")
    click.echo("   3. poetry install")
    click.echo("   4. poetry run python manage.py migrate")
    click.echo("   5. poetry run python manage.py superuser")
    click.echo("   6. poetry run python manage.py runserver")
    click.echo()
    click.echo("🐳 Docker deployment:")
    click.echo(f"   cd {project_name}/docker")
    click.echo("   docker-compose -f docker-compose-local.yaml up -d")
    click.echo()
    click.echo("🤖 AI Documentation (MCP Server):")
    click.echo('   {"mcpServers": {"djangocfg": {"url": "https://mcp.djangocfg.com/mcp"}}}')
    click.echo()
    click.echo("💡 Features included:")
    click.echo("   🤖 AI-native documentation (MCP server)")
    click.echo("   🔧 Type-safe configuration with Pydantic v2")
    click.echo("   🎨 Modern Unfold admin interface")
    click.echo("   📊 Auto-generated API documentation")
    click.echo("   🔐 JWT authentication system")
    click.echo("   🗃️ Multi-database support")
    click.echo("   ⚡ Background task processing (django-rq)")
    click.echo("   🐳 Docker deployment ready")
    click.echo()
    click.echo(f"📚 Documentation: {LIB_SITE_URL}")
    click.echo(f"   {project_name}/docs/ - Local setup guides")


@click.command()
@click.argument("project_name")
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default=".",
    help="Parent directory where to create the project (default: current directory)"
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing directory if it exists"
)
def create_project(project_name: str, path: str, force: bool):
    """
    🚀 Create a new Django project with django-cfg

    Downloads the latest django-cfg template from GitHub and extracts it
    to a new directory with the specified name.

    \b
    Examples:
        django-cfg create-project my_app
        django-cfg create-project my_app --path /projects
        django-cfg create-project my_app --force
    """
    # Validate project name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        click.echo("❌ Invalid project name. Use only letters, numbers, underscores and hyphens.", err=True)
        return

    # Determine target path
    parent_path = Path(path).resolve()
    target_path = parent_path / project_name

    # Check if directory already exists
    if target_path.exists():
        if not force:
            click.echo(f"❌ Directory '{target_path}' already exists. Use --force to overwrite.", err=True)
            return
        else:
            click.echo(f"⚠️  Directory '{target_path}' exists and will be overwritten...")
            shutil.rmtree(target_path)

    temp_archive = None

    try:
        click.echo()
        click.echo(f"🚀 Creating Django project: {project_name}")
        click.echo(f"📁 Target: {target_path}")
        click.echo()

        # Download template from GitHub
        temp_archive = _download_template()

        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)

        # Extract template
        _extract_template(temp_archive, target_path)

        # Show next steps with Rich formatting
        _show_next_steps(target_path, project_name)

    except Exception as e:
        click.echo(f"❌ Error creating project: {e}", err=True)
        # Clean up on error
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)
        raise click.Abort()

    finally:
        # Clean up temp file
        if temp_archive and temp_archive.exists():
            temp_archive.unlink()
