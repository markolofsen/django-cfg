"""
Django CFG Create Project Command

Creates a new Django project using django-cfg sample template.
"""

import click
import shutil
import os
from pathlib import Path
from typing import Optional
import tempfile
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..utils import find_template_archive, validate_project_name

console = Console()


def show_thank_you_message():
    """Display a beautiful thank you message with company info."""
    # Create styled text
    title = Text("Thank you for using django-cfg!", style="bold cyan")
    
    # Company info with clickable link
    company_text = Text()
    company_text.append("Developed by ", style="white")
    company_text.append("Unrealon.com", style="bold blue underline")
    company_text.append(" — Complex parsers on demand", style="white")
    
    link_text = Text()
    link_text.append("🌐 ", style="green")
    link_text.append("https://unrealon.com", style="blue underline")
    
    # Create panel content
    panel_content = Text()
    panel_content.append(title)
    panel_content.append("\n\n")
    panel_content.append(company_text)
    panel_text = Text()
    panel_text.append("\n")
    panel_text.append(link_text)
    panel_content.append(panel_text)
    
    # Display beautiful panel
    console.print()
    console.print(Panel(
        panel_content,
        title="🚀 Django CFG",
        title_align="center",
        border_style="bright_blue",
        padding=(1, 2)
    ))


def extract_template(archive_path: Path, target_path: Path, project_name: str) -> None:
    """Extract template archive to target directory with project name replacements."""
    import zipfile
    
    click.echo(f"📂 Extracting template from archive...")
    
    target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    
    files_extracted = 0
    try:
        with zipfile.ZipFile(archive_path, 'r') as archive:
            for member in archive.namelist():
                # Extract file
                archive.extract(member, target_path)
                files_extracted += 1
                
                # Apply project name replacements to text files
                extracted_file = target_path / member
                if extracted_file.is_file() and should_process_file_for_replacements(extracted_file):
                    replace_project_name(extracted_file, project_name)
        
        click.echo(f"✅ Extracted {files_extracted} files from template")
        
    except zipfile.BadZipFile:
        raise ValueError(f"Invalid template archive: {archive_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract template: {e}")


def should_process_file_for_replacements(file_path: Path) -> bool:
    """Check if file should be processed for project name replacements."""
    text_extensions = {'.py', '.yaml', '.yml', '.json', '.toml', '.txt', '.md', '.html', '.css', '.js', '.conf', '.sh'}
    return file_path.suffix.lower() in text_extensions


def replace_project_name(file_path: Path, project_name: str) -> None:
    """Replace template project name with actual project name."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace common template placeholders
        replacements = {
            "Django CFG Sample": project_name,
            "django-cfg-sample": project_name.lower().replace(" ", "-"),
            "django_cfg_sample": project_name.lower().replace(" ", "_").replace("-", "_"),
            "DjangoCfgSample": "".join(word.capitalize() for word in project_name.replace("-", " ").replace("_", " ").split()),
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except (UnicodeDecodeError, PermissionError, OSError):
        # Skip binary files or files we can't process
        pass




def create_readme(target_path: Path, project_name: str) -> None:
    """Create a README.md file for the new project."""
    readme_content = f"""# {project_name}

A Django project powered by **django-cfg** - the production-ready Django configuration framework.

## 🚀 Features

This project includes:

- **🔧 Type-safe Configuration** - Pydantic v2 models with validation
- **📱 Twilio Integration** - OTP services (WhatsApp, SMS, Email) 
- **📧 Email Services** - SendGrid integration
- **💬 Telegram Bot** - Notifications and alerts
- **🎨 Modern Admin** - Unfold admin interface
- **📊 API Documentation** - Auto-generated OpenAPI/Swagger
- **🔐 JWT Authentication** - Ready-to-use auth system
- **🗃️ Multi-database Support** - With automatic routing
- **⚡ Background Tasks** - Dramatiq task processing
- **🌐 Ngrok Integration** - Easy webhook testing
- **🐳 Docker Ready** - Complete containerization

## 📦 Quick Start

1. **Install Dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy and edit configuration
   cp api/environment/config.dev.yaml api/environment/config.local.yaml
   # Edit config.local.yaml with your settings
   ```

3. **Setup Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Populate Sample Data** (Optional)
   ```bash
   python manage.py populate_sample_data
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

Edit `api/environment/config.dev.yaml` (or create `config.local.yaml`) to configure:

- **Database connections** (PostgreSQL, MySQL, SQLite)
- **Email settings** (SMTP, SendGrid)
- **Twilio credentials** (Account SID, Auth Token, Verify Service SID)
- **Telegram bot** (Bot Token, Chat ID)
- **API keys** (OpenAI, OpenRouter, etc.)
- **Cache settings** (Redis)

## 📱 Twilio OTP Usage

```python
from django_cfg import send_sms_otp, send_whatsapp_otp, send_email_otp, verify_otp

# Send SMS OTP
success, message = send_sms_otp("+1234567890")

# Send WhatsApp OTP with SMS fallback
success, message = send_whatsapp_otp("+1234567890", fallback_to_sms=True)

# Send Email OTP
success, message, code = send_email_otp("user@example.com")

# Verify OTP
is_valid, result = verify_otp("+1234567890", "123456")
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use the production setup
docker-compose -f docker-compose.yml -f docker-compose.nginx.yml up -d
```

## 📚 Documentation

- **Admin Interface**: `http://localhost:8000/admin/`
- **API Documentation**: `http://localhost:8000/api/schema/swagger-ui/`
- **Django CFG Docs**: [djangocfg.com](https://djangocfg.com)

## 🛠️ Development

```bash
# Run with Ngrok for webhook testing
python manage.py runserver_ngrok

# Generate OpenAPI clients
python manage.py generate_openapi_clients

# Translate content (if using i18n)
python manage.py translate_content
```

## 📁 Project Structure

```
{project_name.lower().replace(" ", "_")}/
├── api/                    # Configuration and settings
│   ├── config.py          # Main django-cfg configuration
│   ├── environment/       # Environment-specific configs
│   ├── settings.py        # Generated Django settings
│   └── urls.py           # Root URL configuration
├── apps/                  # Django applications
│   ├── blog/             # Blog app example
│   ├── profiles/         # User profiles
│   └── shop/             # E-commerce example
├── core/                 # Core utilities and management commands
├── docker/               # Docker configuration
├── static/               # Static files
├── templates/            # Django templates
└── manage.py            # Django management script
```

## 🤝 Contributing

This project uses **django-cfg** for configuration management. 
For more information, visit: [https://github.com/markolofsen/django-cfg](https://github.com/markolofsen/django-cfg)

## 📄 License

MIT License - see LICENSE file for details.

---

**Powered by django-cfg** 🚀
"""
    
    readme_path = target_path / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def run_command(target_path: Path, command: list, description: str, use_poetry: bool = True, check: bool = True) -> tuple[bool, str]:
    """
    Universal function to run commands with Poetry or pip.
    
    Args:
        target_path: Project directory
        command: Command to run (without poetry/python prefix)
        description: Description for user feedback
        use_poetry: Use Poetry if True, pip/python if False
        check: Raise exception on error if True
        
    Returns:
        (success: bool, output: str)
    """
    try:
        if use_poetry:
            cmd = ["poetry", "run"] + command
        else:
            # For pip/python commands, use system python
            if command[0] == "python":
                cmd = [sys.executable] + command[1:]
            else:
                cmd = command
        
        result = subprocess.run(
            cmd,
            cwd=target_path,
            check=check,
            capture_output=True,
            text=True
        )
        
        return True, result.stdout
        
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"


def install_dependencies(target_path: Path, use_poetry: bool = True) -> bool:
    """Install project dependencies using Poetry or pip."""
    click.echo("📦 Installing dependencies...")
    
    if use_poetry:
        success, output = run_command(target_path, ["poetry", "install"], "Installing with Poetry", use_poetry=False)
    else:
        success, output = run_command(target_path, ["python", "-m", "pip", "install", "-r", "requirements.txt"], "Installing with pip", use_poetry=False)
    
    if success:
        click.echo("✅ Dependencies installed successfully")
        return True
    else:
        click.echo(f"⚠️  Warning: Failed to install dependencies: {output}", err=True)
        return False


def setup_project_structure(target_path: Path) -> bool:
    """Create necessary directories for the project."""
    try:
        # Create db directory for SQLite database
        db_dir = target_path / "db"
        db_dir.mkdir(exist_ok=True)
        click.echo(f"📁 Created database directory: {db_dir}")
        
        # Create cache directory
        cache_dir = target_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        click.echo(f"📁 Created cache directory: {cache_dir}")
        
        return True
    except Exception as e:
        click.echo(f"⚠️  Warning: Failed to create project directories: {e}", err=True)
        return False


def run_initial_migrations(target_path: Path, use_poetry: bool = True) -> bool:
    """Run initial Django migrations."""
    click.echo("🔄 Running initial migrations...")
    
    # Try cli migrator first, fallback to manage.py migrate
    success, output = run_command(target_path, ["cli", "migrator"], "Running migrations", use_poetry, check=False)
    
    if not success:
        click.echo("   Falling back to manage.py migrate...")
        success, output = run_command(target_path, ["python", "manage.py", "migrate"], "Running migrations", use_poetry)
    
    if success:
        click.echo("✅ Initial migrations completed successfully")
        return True
    else:
        click.echo(f"⚠️  Warning: Failed to run migrations: {output}", err=True)
        return False


def populate_sample_data(target_path: Path, use_poetry: bool = True) -> bool:
    """Populate database with sample data."""
    click.echo("👥 Populating sample data (users, blog posts, products)...")
    
    success, output = run_command(
        target_path, 
        ["python", "manage.py", "populate_sample_data", "--users", "10", "--posts", "20", "--products", "30"],
        "Populating sample data",
        use_poetry
    )
    
    if success:
        click.echo("✅ Sample data populated successfully")
        click.echo("   📝 Created 10 test users, 20 blog posts, 30 products")
        return True
    else:
        click.echo(f"⚠️  Warning: Failed to populate sample data: {output}", err=True)
        return False


@click.command()
@click.argument("project_name")
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default=".",
    help="Directory where to create the project (default: current directory)"
)
@click.option(
    "--no-deps",
    is_flag=True,
    help="Skip automatic dependency installation"
)
@click.option(
    "--use-pip",
    is_flag=True,
    help="Use pip instead of Poetry for dependency installation"
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing directory if it exists"
)
@click.option(
    "--no-setup",
    is_flag=True,
    help="Skip automatic project setup (directories, migrations)"
)
@click.option(
    "--no-sample-data",
    is_flag=True,
    help="Skip sample data population (users, posts, products)"
)
def create_project(project_name: str, path: str, no_deps: bool, use_pip: bool, force: bool, no_setup: bool, no_sample_data: bool):
    """
    🚀 Create a new Django project with django-cfg
    
    Creates a complete Django project with type-safe configuration,
    modern admin interface, API documentation, and production-ready setup.
    
    PROJECT_NAME: Name of the new Django project
    
    Examples:
    
        # Create project in current directory
        django-cfg create-project "My Awesome Project"
        
        # Create project in specific directory  
        django-cfg create-project "My Project" --path ./projects/
        
        # Skip dependency installation
        django-cfg create-project "My Project" --no-deps
        
        # Use pip instead of Poetry
        django-cfg create-project "My Project" --use-pip
        
        # Skip automatic setup (directories, migrations)
        django-cfg create-project "My Project" --no-setup
        
        # Skip sample data creation (users, posts, products)
        django-cfg create-project "My Project" --no-sample-data
    """
    
    # Validate project name
    if not validate_project_name(project_name):
        click.echo("❌ Invalid project name", err=True)
        return
    
    # Determine target path
    base_path = Path(path).resolve()
    project_dir_name = project_name.lower().replace(" ", "_").replace("-", "_")
    target_path = base_path / project_dir_name
    
    # Check if target directory exists
    if target_path.exists():
        if not force:
            click.echo(f"❌ Directory '{target_path}' already exists. Use --force to overwrite.", err=True)
            return
        else:
            click.echo(f"⚠️  Removing existing directory '{target_path}'...")
            shutil.rmtree(target_path)
    
    try:
        # Get template archive path
        archive_path = find_template_archive()
        if not archive_path:
            raise FileNotFoundError(
                "Could not find django_sample.zip template archive. "
                "Please ensure django-cfg is properly installed or run 'python scripts/template_manager.py create' in development."
            )
        click.echo(f"📋 Using template archive: {archive_path.name}")
        
        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Extract template files
        extract_template(archive_path, target_path, project_name)
        
        # Create additional files
        create_readme(target_path, project_name)
        
        click.echo(f"✅ Project '{project_name}' created successfully!")
        click.echo(f"📁 Location: {target_path}")
        
        # Setup project structure
        if not no_setup:
            click.echo("\n🔧 Setting up project structure...")
            setup_project_structure(target_path)
        
        # Install dependencies if requested
        deps_installed = False
        if not no_deps:
            install_success = install_dependencies(target_path, not use_pip)
            if install_success:
                deps_installed = True
            else:
                click.echo("💡 You can install dependencies manually later:")
                if not use_pip:
                    click.echo("   poetry install")
                else:
                    click.echo("   pip install -r requirements.txt")
        
        # Run initial setup if dependencies were installed
        if deps_installed and not no_setup:
            click.echo("\n🔄 Running initial project setup...")
            migration_success = run_initial_migrations(target_path, not use_pip)
            
            if migration_success:
                # Populate sample data if requested
                if not no_sample_data:
                    sample_data_success = populate_sample_data(target_path, not use_pip)
                    if sample_data_success:
                        click.echo("✅ Project is ready to use with sample data!")
                        click.echo("💡 Login credentials: username/password for any test user")
                    else:
                        click.echo("✅ Project is ready to use!")
                        click.echo("💡 You can populate sample data later:")
                        if not use_pip:
                            click.echo("   poetry run python manage.py populate_sample_data")
                        else:
                            click.echo("   python manage.py populate_sample_data")
                else:
                    click.echo("✅ Project is ready to use!")
            else:
                click.echo("💡 You can run migrations manually later:")
                if not use_pip:
                    click.echo("   poetry run cli migrator")
                else:
                    click.echo("   python manage.py migrate")
        
        # Show next steps
        click.echo("\n🎉 Your Django CFG project is ready!")
        click.echo("\n📋 Next steps:")
        click.echo(f"   cd {project_dir_name}")
        
        if no_deps:
            if not use_pip:
                click.echo("   poetry install")
            else:
                click.echo("   pip install -r requirements.txt")
        
        if no_setup or not deps_installed:
            click.echo("   # Edit api/environment/config.dev.yaml with your settings")
            if not deps_installed:
                if not use_pip:
                    click.echo("   poetry run cli migrator")
                else:
                    click.echo("   python manage.py migrate")
            click.echo("   python manage.py createsuperuser")
        else:
            click.echo("   # Edit api/environment/config.dev.yaml with your settings")
            click.echo("   python manage.py createsuperuser")
        
        if not use_pip:
            click.echo("   poetry run cli runserver")
        else:
            click.echo("   python manage.py runserver")
        
        click.echo("\n💡 Features included:")
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
        
        # click.echo(f"\n📚 Documentation: https://djangocfg.com")
        
        # Beautiful thank you message
        show_thank_you_message()
        
    except FileNotFoundError as e:
        click.echo(f"❌ Template archive not found: {e}", err=True)
        click.echo("💡 Make sure django-cfg is properly installed")
        click.echo("💡 In development, run: python scripts/template_manager.py create")
        
    except (ValueError, RuntimeError) as e:
        click.echo(f"❌ Template error: {e}", err=True)
        # Clean up on error
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {e}", err=True)
        # Clean up on error
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)
