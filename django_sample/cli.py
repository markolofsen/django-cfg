#!/usr/bin/env python
"""
Poetry CLI commands for Django CFG Sample Project.
Enhanced CLI with Click for better UX.
"""

import os
import click
from django.core.management import execute_from_command_line


def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')


@click.group()
def cli():
    """Django CFG Sample Project CLI."""
    pass


# === Standard Django Commands ===

@cli.command()
@click.option('--port', default='8000', help='Port to run server on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def runserver(port, host):
    """Run Django development server."""
    setup_django()
    execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])


@cli.command()
@click.option('--database', help='Database to migrate')
@click.option('--fake', is_flag=True, help='Mark migrations as run without actually running them')
def migrate(database, fake):
    """Run Django migrations."""
    setup_django()
    cmd = ['manage.py', 'migrate']
    if database:
        cmd.extend(['--database', database])
    if fake:
        cmd.append('--fake')
    execute_from_command_line(cmd)


@cli.command()
@click.argument('app_labels', nargs=-1)
@click.option('--dry-run', is_flag=True, help='Just show what migrations would be made')
@click.option('--empty', is_flag=True, help='Create an empty migration')
def makemigrations(app_labels, dry_run, empty):
    """Create Django migrations."""
    setup_django()
    cmd = ['manage.py', 'makemigrations']
    if dry_run:
        cmd.append('--dry-run')
    if empty:
        cmd.append('--empty')
    cmd.extend(app_labels)
    execute_from_command_line(cmd)


@cli.command()
@click.option('--username', help='Username for the superuser')
@click.option('--email', help='Email for the superuser')
def createsuperuser(username, email):
    """Create Django superuser."""
    setup_django()
    cmd = ['manage.py', 'createsuperuser']
    if username:
        cmd.extend(['--username', username])
    if email:
        cmd.extend(['--email', email])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--noinput', is_flag=True, help='Do not prompt for input')
@click.option('--clear', is_flag=True, help='Clear existing files before collecting')
def collectstatic(noinput, clear):
    """Collect Django static files."""
    setup_django()
    cmd = ['manage.py', 'collectstatic']
    if noinput:
        cmd.append('--noinput')
    if clear:
        cmd.append('--clear')
    execute_from_command_line(cmd)


# === Django CFG Commands ===

@cli.command()
@click.option('--auto', is_flag=True, default=True, help='Run automatic migration')
@click.option('--database', help='Specific database to migrate')
def migrator(auto, database):
    """Run Django CFG smart migrator with automatic routing."""
    setup_django()
    cmd = ['manage.py', 'migrator']
    if auto:
        cmd.append('--auto')
    if database:
        cmd.extend(['--database', database])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--include-secrets', is_flag=True, help='Include sensitive information')
def show_config(format, include_secrets):
    """Show Django CFG configuration."""
    setup_django()
    cmd = ['manage.py', 'show_config', '--format', format]
    if include_secrets:
        cmd.append('--include-secrets')
    execute_from_command_line(cmd)


@cli.command()
@click.option('--show-details', is_flag=True, help='Show detailed configuration information')
@click.option('--check-connections', is_flag=True, help='Test database and cache connections')
def validate_config(show_details, check_connections):
    """Validate Django CFG configuration."""
    setup_django()
    cmd = ['manage.py', 'validate_config']
    if show_details:
        cmd.append('--show-details')
    if check_connections:
        cmd.append('--check-connections')
    execute_from_command_line(cmd)


@cli.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def show_urls(format):
    """Show all URL patterns."""
    setup_django()
    execute_from_command_line(['manage.py', 'show_urls', '--format', format])


@cli.command()
def check_settings():
    """Check Django CFG settings."""
    setup_django()
    execute_from_command_line(['manage.py', 'check_settings'])


@cli.command()
@click.option('--script-name', help='Script name to run')
@click.option('--list', 'list_scripts', is_flag=True, help='List available scripts')
def script(script_name, list_scripts):
    """Run Django CFG interactive script runner."""
    setup_django()
    cmd = ['manage.py', 'script']
    if script_name:
        cmd.extend(['--script', script_name])
    if list_scripts:
        cmd.append('--list')
    execute_from_command_line(cmd)


@cli.command()
@click.option('--email', help='Email for the superuser')
@click.option('--username', help='Username for the superuser')
def superuser(email, username):
    """Create superuser with Django CFG enhanced features."""
    setup_django()
    cmd = ['manage.py', 'superuser']
    if email:
        cmd.extend(['--email', email])
    if username:
        cmd.extend(['--username', username])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--to', help='Email address to send test email to')
def test_email(to):
    """Test email configuration."""
    setup_django()
    cmd = ['manage.py', 'test_email']
    if to:
        cmd.extend(['--to', to])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--message', help='Test message to send')
def test_telegram(message):
    """Test Telegram configuration."""
    setup_django()
    cmd = ['manage.py', 'test_telegram']
    if message:
        cmd.extend(['--message', message])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--username', help='Username to create token for')
def create_token(username):
    """Create authentication token."""
    setup_django()
    cmd = ['manage.py', 'create_token']
    if username:
        cmd.extend(['--username', username])
    execute_from_command_line(cmd)


@cli.command()
@click.option('--type', 'gen_type', help='Type of code to generate')
def generate(gen_type):
    """Run Django CFG code generator."""
    setup_django()
    cmd = ['manage.py', 'generate']
    if gen_type:
        cmd.extend(['--type', gen_type])
    execute_from_command_line(cmd)


# Entry points for individual commands (for Poetry scripts)
def runserver():
    """Entry point for runserver command."""
    cli(['runserver'])

def migrate():
    """Entry point for migrate command."""
    cli(['migrate'])

def makemigrations():
    """Entry point for makemigrations command."""
    cli(['makemigrations'])

def createsuperuser():
    """Entry point for createsuperuser command."""
    cli(['createsuperuser'])

def collectstatic():
    """Entry point for collectstatic command."""
    cli(['collectstatic'])

def migrator():
    """Entry point for migrator command."""
    cli(['migrator'])

def show_config():
    """Entry point for show-config command."""
    cli(['show-config'])

def validate_config():
    """Entry point for validate-config command."""
    cli(['validate-config'])

def show_urls():
    """Entry point for show-urls command."""
    cli(['show-urls'])

def check_settings():
    """Entry point for check-settings command."""
    cli(['check-settings'])

def script():
    """Entry point for script command."""
    cli(['script'])

def superuser():
    """Entry point for superuser command."""
    cli(['superuser'])

def test_email():
    """Entry point for test-email command."""
    cli(['test-email'])

def test_telegram():
    """Entry point for test-telegram command."""
    cli(['test-telegram'])

def create_token():
    """Entry point for create-token command."""
    cli(['create-token'])

def generate():
    """Entry point for generate command."""
    cli(['generate'])


if __name__ == '__main__':
    cli()