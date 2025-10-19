"""
Django CFG Create Project Command

Creates a new Django project by downloading from GitHub.
"""

import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import click

# GitHub template URL
TEMPLATE_URL = "https://github.com/markolofsen/django-cfg/archive/refs/heads/main.zip"


def download_template(url: str) -> Path:
    """Download template archive from GitHub."""
    click.echo("📥 Downloading template from GitHub...")

    try:
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_path = Path(temp_file.name)

        # Download with progress
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192

            with open(temp_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        click.echo(f"\r   Progress: {progress:.1f}%", nl=False)

        click.echo("\n✅ Template downloaded successfully")
        return temp_path

    except Exception as e:
        raise RuntimeError(f"Failed to download template: {e}")


def extract_template(archive_path: Path, target_path: Path) -> None:
    """Extract template archive to target directory."""
    click.echo("📂 Extracting template...")

    try:
        with zipfile.ZipFile(archive_path, 'r') as archive:
            members = archive.namelist()

            # Find the root folder name (django-cfg-main)
            root_folder = members[0].split('/')[0] if members else None

            if not root_folder:
                raise ValueError("Archive structure is invalid")

            # Path to examples directory: django-cfg-main/examples/
            examples_prefix = f"{root_folder}/examples/"

            # Extract files from examples/ folder (preserving django/ and docker/ subdirectories)
            extracted_files = 0
            for member in members:
                # Skip if not in examples path
                if not member.startswith(examples_prefix):
                    continue

                # Calculate relative path (remove examples_prefix, keep django/ and docker/)
                relative_path = member[len(examples_prefix):]

                # Skip empty paths (directory markers)
                if not relative_path:
                    continue

                # Skip docker volumes directory
                if relative_path.startswith("docker/volumes/"):
                    continue

                # Skip .gitignore files
                if relative_path.endswith(".gitignore"):
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

        click.echo(f"✅ Template extracted successfully ({extracted_files} files)")

    except zipfile.BadZipFile:
        raise ValueError("Invalid template archive")
    except Exception as e:
        raise RuntimeError(f"Failed to extract template: {e}")


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default=".",
    help="Directory where to create the project (default: current directory)"
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files if they exist"
)
def create_project(path: str, force: bool):
    """
    🚀 Create a new Django project with django-cfg

    Downloads the latest django-cfg template from GitHub and extracts it.

    Examples:

        # Extract to current directory
        django-cfg create-project

        # Extract to specific directory
        django-cfg create-project --path ./my-project/

        # Overwrite existing files
        django-cfg create-project --force
    """

    # Determine parent path and project folder name
    parent_path = Path(path).resolve()

    # Create django-project folder inside the specified path
    target_path = parent_path / "django-project"

    # Check if django-project directory already exists
    if target_path.exists():
        if not force:
            click.echo(f"❌ Directory '{target_path}' already exists. Use --force to overwrite.", err=True)
            return
        else:
            click.echo(f"⚠️  Directory '{target_path}' exists and will be overwritten...")
            shutil.rmtree(target_path)

    temp_archive = None

    try:
        click.echo("🚀 Creating Django project from GitHub")
        click.echo(f"📁 Target location: {target_path}")
        click.echo()

        # Download template from GitHub
        temp_archive = download_template(TEMPLATE_URL)

        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)

        # Extract template
        extract_template(temp_archive, target_path)

        click.echo()
        click.echo("✅ Project created successfully!")
        click.echo(f"📁 Location: {target_path}")

        # Show next steps
        click.echo()
        click.echo("📋 Next steps:")
        click.echo(f"   cd {target_path}/django")
        click.echo("   poetry install  # or: pip install -r requirements.txt")
        click.echo("   python manage.py migrate")
        click.echo("   python manage.py createsuperuser")
        click.echo("   python manage.py runserver")
        click.echo()
        click.echo("🐳 Docker deployment:")
        click.echo(f"   cd {target_path}/docker")
        click.echo("   docker-compose up -d")

        click.echo()
        click.echo("💡 Features included:")
        click.echo("   🔧 Type-safe configuration with Pydantic v2")
        click.echo("   📱 Twilio integration (WhatsApp, SMS, Email OTP)")
        click.echo("   📧 Email services with SendGrid")
        click.echo("   💬 Telegram bot integration")
        click.echo("   🎨 Modern Unfold admin interface")
        click.echo("   📊 Auto-generated API documentation")
        click.echo("   🔐 JWT authentication system")
        click.echo("   🗃️ Multi-database support with routing")
        click.echo("   ⚡ Background task processing")
        click.echo("   🐳 Docker deployment ready")

        click.echo()
        click.echo("📚 Documentation: https://github.com/markolofsen/django-cfg")
        click.echo("🌐 Developed by Unrealon.com — Complex parsers on demand")

    except Exception as e:
        click.echo(f"❌ Error creating project: {e}", err=True)
        # Clean up on error
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)
        raise

    finally:
        # Clean up temp file
        if temp_archive and temp_archive.exists():
            temp_archive.unlink()
