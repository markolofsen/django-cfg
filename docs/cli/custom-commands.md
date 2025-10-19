---
title: Custom CLI Commands
description: Django-CFG CLI custom commands commands. Command-line interface for custom cli commands with examples, options, and production workflows.
sidebar_label: Custom Commands
sidebar_position: 3
keywords:
  - django-cfg custom commands
  - django-cfg command custom commands
  - cli custom commands
---

# Custom CLI Commands

Learn how to create custom CLI commands for your Django-CFG projects using Click and integrate them with the existing CLI system.

## Overview

Django-CFG provides a flexible system for creating custom CLI commands that integrate seamlessly with the existing CLI infrastructure. You can:

- **Extend the CLI** with project-specific commands
- **Use Click decorators** for rich command-line interfaces
- **Access Django-CFG configuration** within commands
- **Integrate with Rich** for beautiful output
- **Share commands** across team members

## Quick Start

### 1. Create Command Directory

In your Django-CFG project, create a management commands directory:

```bash
mkdir -p core/management/commands/
touch core/management/__init__.py
touch core/management/commands/__init__.py
```

### 2. Basic Custom Command

Create `core/management/commands/hello.py`:

```python
"""
Custom Hello Command Example
"""

import click
from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel

console = Console()


class Command(BaseCommand):
    help = "Say hello with Django-CFG style"

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='World',
            help='Name to greet'
        )
        parser.add_argument(
            '--style',
            choices=['simple', 'fancy', 'panel'],
            default='simple',
            help='Output style'
        )

    def handle(self, *args, **options):
        name = options['name']
        style = options['style']
        
        if style == 'simple':
            self.stdout.write(f"Hello, {name}!")
        elif style == 'fancy':
            console.print(f"✨ Hello, [bold cyan]{name}[/bold cyan]! ✨")
        elif style == 'panel':
            console.print(Panel(
                f"Hello, [bold green]{name}[/bold green]!",
                title="🚀 Django-CFG Greeting",
                border_style="bright_blue"
            ))
```

### 3. Use the Command

```bash
# Basic usage
python manage.py hello

# With options
python manage.py hello --name "Django Developer" --style fancy

# With Poetry
poetry run python manage.py hello --name "Team" --style panel
```

## Advanced Command Patterns

### Click Integration

Create more sophisticated commands using Click directly:

```python
"""
Advanced Click Command with Django-CFG Integration
"""

import click
from django.core.management.base import BaseCommand
from django.conf import settings
from rich.console import Console
from rich.table import Table
from rich.progress import track

from api.config import config  # Your Django-CFG config

console = Console()


class Command(BaseCommand):
    help = "Advanced command with Click integration"

    def add_arguments(self, parser):
        # Use Click for argument parsing
        pass

    def handle(self, *args, **options):
        # Delegate to Click command
        cli_main()


@click.group()
def cli_main():
    """Advanced Django-CFG command group."""
    pass


@cli_main.command()
@click.option('--database', '-d', help='Database to analyze')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze_db(database: str, verbose: bool):
    """Analyze database performance and structure."""
    
    # Access Django-CFG configuration
    db_config = config.databases.get(database or 'default')
    if not db_config:
        console.print(f"❌ Database '{database}' not found", style="red")
        return
    
    console.print(f"🔍 Analyzing database: [cyan]{database or 'default'}[/cyan]")
    
    # Create rich table
    table = Table(title="Database Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # Simulate analysis with progress
    for i in track(range(10), description="Analyzing..."):
        # Your analysis logic here
        pass
    
    # Add results to table
    table.add_row("Engine", db_config.engine)
    table.add_row("Name", db_config.name)
    table.add_row("Tables", "42")  # Your logic here
    
    console.print(table)


@cli_main.command()
@click.argument('service_name')
@click.option('--timeout', default=30, help='Timeout in seconds')
def test_service(service_name: str, timeout: int):
    """Test external service connectivity."""
    
    console.print(f"🧪 Testing service: [yellow]{service_name}[/yellow]")
    
    # Access service configuration from Django-CFG
    services = {
        'twilio': config.twilio if hasattr(config, 'twilio') else None,
        'sendgrid': config.email if hasattr(config, 'email') else None,
        'telegram': config.telegram if hasattr(config, 'telegram') else None,
    }
    
    service_config = services.get(service_name.lower())
    if not service_config:
        console.print(f"❌ Service '{service_name}' not configured", style="red")
        return
    
    # Test service (implement your logic)
    with console.status(f"Testing {service_name}..."):
        # Your testing logic here
        import time
        time.sleep(2)  # Simulate test
    
    console.print(f"✅ Service '{service_name}' is working!", style="green")
```

### Configuration Access

Access Django-CFG configuration within commands:

```python
"""
Command that uses Django-CFG configuration
"""

from django.core.management.base import BaseCommand
from rich.console import Console
from rich.json import JSON

from api.config import config

console = Console()


class Command(BaseCommand):
    help = "Show Django-CFG configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            '--section',
            help='Configuration section to show'
        )
        parser.add_argument(
            '--format',
            choices=['json', 'yaml', 'table'],
            default='json',
            help='Output format'
        )

    def handle(self, *args, **options):
        section = options.get('section')
        format_type = options['format']
        
        if section:
            # Show specific section
            if hasattr(config, section):
                data = getattr(config, section)
                if hasattr(data, 'model_dump'):
                    data = data.model_dump()
            else:
                console.print(f"❌ Section '{section}' not found", style="red")
                return
        else:
            # Show all configuration
            data = config.model_dump()
        
        if format_type == 'json':
            console.print(JSON.from_data(data))
        elif format_type == 'yaml':
            import yaml
            console.print(yaml.dump(data, default_flow_style=False))
        elif format_type == 'table':
            # Create table representation
            from rich.table import Table
            table = Table(title="Django-CFG Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            def add_to_table(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, (dict, list)):
                            add_to_table(value, full_key)
                        else:
                            table.add_row(full_key, str(value))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        add_to_table(item, f"{prefix}[{i}]")
            
            add_to_table(data)
            console.print(table)
```

## Rich Output Examples

### Progress Bars

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def handle(self, *args, **options):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        
        task = progress.add_task("Processing...", total=100)
        
        for i in range(100):
            # Your work here
            progress.update(task, advance=1)
            time.sleep(0.01)
    
    console.print("✅ Processing complete!", style="green")
```

### Interactive Prompts

```python
import click

def handle(self, *args, **options):
    # Simple confirmation
    if click.confirm('Do you want to continue?'):
        console.print("Continuing...", style="green")
    
    # Text input with validation
    email = click.prompt(
        'Email address',
        type=click.STRING,
        default='admin@example.com'
    )
    
    # Password input (hidden)
    password = click.prompt(
        'Password',
        type=click.STRING,
        hide_input=True,
        confirmation_prompt=True
    )
    
    # Choice selection
    environment = click.prompt(
        'Environment',
        type=click.Choice(['dev', 'staging', 'prod']),
        default='dev'
    )
```

### Status and Spinners

```python
from rich.console import Console
from rich.status import Status
import time

console = Console()

def handle(self, *args, **options):
    with console.status("[bold green]Working on tasks...") as status:
        time.sleep(2)
        status.update("[bold blue]Almost done...")
        time.sleep(2)
    
    console.print("✅ All done!", style="green")
```

## 🔌 Integration Patterns

### Database Operations

```python
"""
Command for database operations
"""

from django.core.management.base import BaseCommand
from django.db import connections
from rich.console import Console
from rich.table import Table

console = Console()


class Command(BaseCommand):
    help = "Database utilities"

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['list', 'test', 'info'])
        parser.add_argument('--database', help='Database alias')

    def handle(self, *args, **options):
        action = options['action']
        database = options.get('database', 'default')
        
        if action == 'list':
            self.list_databases()
        elif action == 'test':
            self.test_connection(database)
        elif action == 'info':
            self.show_info(database)

    def list_databases(self):
        """List all configured databases."""
        table = Table(title="Configured Databases")
        table.add_column("Alias", style="cyan")
        table.add_column("Engine", style="green")
        table.add_column("Name", style="yellow")
        
        for alias in connections:
            conn = connections[alias]
            table.add_row(
                alias,
                conn.settings_dict['ENGINE'],
                conn.settings_dict['NAME']
            )
        
        console.print(table)

    def test_connection(self, database: str):
        """Test database connection."""
        try:
            conn = connections[database]
            conn.ensure_connection()
            console.print(f"✅ Connection to '{database}' successful!", style="green")
        except Exception as e:
            console.print(f"❌ Connection to '{database}' failed: {e}", style="red")

    def show_info(self, database: str):
        """Show database information."""
        conn = connections[database]
        settings = conn.settings_dict
        
        table = Table(title=f"Database Info: {database}")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in settings.items():
            if key == 'PASSWORD':
                value = '***' if value else 'Not set'
            table.add_row(key, str(value))
        
        console.print(table)
```

### Service Testing

```python
"""
Command for testing external services
"""

from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel
import requests
import time

console = Console()


class Command(BaseCommand):
    help = "Test external service integrations"

    def add_arguments(self, parser):
        parser.add_argument('service', choices=['all', 'twilio', 'sendgrid', 'telegram'])
        parser.add_argument('--timeout', type=int, default=10)

    def handle(self, *args, **options):
        service = options['service']
        timeout = options['timeout']
        
        if service == 'all':
            self.test_all_services(timeout)
        else:
            self.test_service(service, timeout)

    def test_service(self, service: str, timeout: int):
        """Test individual service."""
        console.print(f"🧪 Testing {service.title()} service...")
        
        try:
            with console.status(f"Connecting to {service}..."):
                # Implement service-specific testing
                if service == 'twilio':
                    self.test_twilio(timeout)
                elif service == 'sendgrid':
                    self.test_sendgrid(timeout)
                elif service == 'telegram':
                    self.test_telegram(timeout)
            
            console.print(Panel(
                f"✅ {service.title()} service is working correctly!",
                title="Success",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(Panel(
                f"❌ {service.title()} service failed: {str(e)}",
                title="Error",
                border_style="red"
            ))

    def test_twilio(self, timeout: int):
        """Test Twilio service."""
        from api.config import config
        
        if not hasattr(config, 'twilio'):
            raise ValueError("Twilio not configured")
        
        # Implement Twilio testing logic
        time.sleep(1)  # Simulate API call

    def test_sendgrid(self, timeout: int):
        """Test SendGrid service."""
        # Implement SendGrid testing logic
        time.sleep(1)  # Simulate API call

    def test_telegram(self, timeout: int):
        """Test Telegram service."""
        # Implement Telegram testing logic
        time.sleep(1)  # Simulate API call
```

## Command Distribution

### Packaging Commands

Create reusable command packages:

```python
# commands/package.py
"""
Reusable command package for Django-CFG projects
"""

from django.core.management.base import BaseCommand
from rich.console import Console

console = Console()


class DjangoCfgCommand(BaseCommand):
    """Base class for Django-CFG commands."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
    
    def success(self, message: str):
        """Print success message."""
        self.console.print(f"✅ {message}", style="green")
    
    def error(self, message: str):
        """Print error message."""
        self.console.print(f"❌ {message}", style="red")
    
    def warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠️ {message}", style="yellow")
    
    def info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ️ {message}", style="blue")


# Your command inherits from DjangoCfgCommand
class Command(DjangoCfgCommand):
    help = "Example command using base class"
    
    def handle(self, *args, **options):
        self.info("Starting process...")
        self.success("Process completed!")
```

### Sharing Commands

Create a commands package for your team:

```python
# team_commands/setup.py
from setuptools import setup, find_packages

setup(
    name="mycompany-django-cfg-commands",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "django-cfg",
        "rich",
        "click",
    ],
    entry_points={
        'console_scripts': [
            'mycompany-deploy=team_commands.deploy:main',
        ],
    },
)
```

## Best Practices

### 1. Use Rich for Output

```python
# Good: Rich formatting
console.print("✅ Success!", style="green")

# Avoid: Plain text
print("Success!")
```

### 2. Handle Errors Gracefully

```python
def handle(self, *args, **options):
    try:
        # Your logic here
        pass
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise CommandError(f"Command failed: {e}")
```

### 3. Use Progress Indicators

```python
from rich.progress import track

def handle(self, *args, **options):
    items = range(100)
    
    for item in track(items, description="Processing..."):
        # Your work here
        time.sleep(0.01)
```

### 4. Validate Configuration

```python
def handle(self, *args, **options):
    from api.config import config
    
    # Validate required configuration
    if not hasattr(config, 'database'):
        raise CommandError("Database configuration missing")
    
    # Continue with command logic
```

### 5. Use Type Hints

```python
from typing import Any, Dict, Optional

def handle(self, *args: Any, **options: Dict[str, Any]) -> None:
    name: Optional[str] = options.get('name')
    count: int = options.get('count', 10)
    
    # Your logic here
```

## Related Documentation

- [**CLI Introduction**](./introduction.md) - Overview and installation
- [**Commands Reference**](./commands/overview.md) - Built-in commands
- [**Configuration Guide**](/fundamentals/configuration) - Access configuration
- [**First Project**](/getting-started/first-project) - See commands in action

## External Resources

- [**Click Documentation**](https://click.palletsprojects.com/) - Click framework
- [**Rich Documentation**](https://rich.readthedocs.io/) - Rich terminal formatting
- [**Django Management Commands**](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/) - Django commands

Create powerful, beautiful CLI commands that make your Django-CFG projects even more productive! 🚀
