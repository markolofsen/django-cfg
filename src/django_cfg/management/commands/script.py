"""
Script Command for Django Config Toolkit
Run custom scripts and manage Django applications.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Run custom scripts and manage Django applications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--script',
            type=str,
            help='Script name to run'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available scripts'
        )
        parser.add_argument(
            '--create',
            type=str,
            help='Create new script template'
        )
        parser.add_argument(
            '--shell',
            action='store_true',
            help='Open Django shell'
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Run Django system check'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_scripts()
        elif options['create']:
            self.create_script_template(options['create'])
        elif options['shell']:
            self.open_django_shell()
        elif options['check']:
            self.run_django_check()
        elif options['script']:
            self.run_script(options['script'])
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with script options"""
        self.stdout.write(self.style.SUCCESS('\n📜 Script Management Tool - Django Config Toolkit\n'))

        choices = [
            questionary.Choice('📋 List Available Scripts', value='list'),
            questionary.Choice('➕ Create New Script', value='create'),
            questionary.Choice('▶️  Run Script', value='run'),
            questionary.Choice('🐚 Open Django Shell', value='shell'),
            questionary.Choice('🔍 Run System Check', value='check'),
            questionary.Choice('🧹 Clean Project', value='clean'),
            questionary.Choice('📊 Show Project Info', value='info'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        choice = questionary.select(
            'Select option:',
            choices=choices
        ).ask()

        if choice == 'list':
            self.list_scripts()
        elif choice == 'create':
            self.create_script_interactive()
        elif choice == 'run':
            self.run_script_interactive()
        elif choice == 'shell':
            self.open_django_shell()
        elif choice == 'check':
            self.run_django_check()
        elif choice == 'clean':
            self.clean_project()
        elif choice == 'info':
            self.show_project_info()
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return

    def list_scripts(self):
        """List available scripts"""
        self.stdout.write(self.style.SUCCESS('📋 Available Scripts\n'))
        
        # Check for scripts directory
        scripts_dir = Path('scripts')
        if not scripts_dir.exists():
            self.stdout.write('  📁 No scripts directory found')
            self.stdout.write('  💡 Use --create to create your first script')
            return
        
        # List Python scripts
        python_scripts = list(scripts_dir.glob('*.py'))
        if python_scripts:
            self.stdout.write('  🐍 Python Scripts:')
            for script in python_scripts:
                if script.name != '__init__.py':
                    self.stdout.write(f'    - {script.stem}')
        else:
            self.stdout.write('  🐍 No Python scripts found')
        
        # List shell scripts
        shell_scripts = list(scripts_dir.glob('*.sh'))
        if shell_scripts:
            self.stdout.write('  🐚 Shell Scripts:')
            for script in shell_scripts:
                self.stdout.write(f'    - {script.stem}')
        
        # List other scripts
        other_scripts = [s for s in scripts_dir.iterdir() if s.is_file() and s.suffix not in ['.py', '.sh']]
        if other_scripts:
            self.stdout.write('  📄 Other Scripts:')
            for script in other_scripts:
                self.stdout.write(f'    - {script.name}')

    def create_script_interactive(self):
        """Create script interactively"""
        self.stdout.write(self.style.SUCCESS('➕ Create New Script\n'))
        
        # Get script name
        script_name = questionary.text('Script name:').ask()
        if not script_name:
            self.stdout.write(self.style.ERROR('❌ Script name is required'))
            return
        
        # Get script type
        script_type = questionary.select(
            'Script type:',
            choices=['Python Script', 'Shell Script', 'Django Management Command']
        ).ask()
        
        # Create script
        if script_type == 'Python Script':
            self.create_python_script(script_name)
        elif script_type == 'Shell Script':
            self.create_shell_script(script_name)
        elif script_type == 'Django Management Command':
            self.create_django_command(script_name)

    def create_script_template(self, script_name):
        """Create script template"""
        self.create_python_script(script_name)

    def create_python_script(self, script_name):
        """Create Python script template"""
        # Create scripts directory
        scripts_dir = Path('scripts')
        scripts_dir.mkdir(exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = scripts_dir / '__init__.py'
        if not init_file.exists():
            init_file.touch()
        
        # Create script file
        script_path = scripts_dir / f'{script_name}.py'
        
        script_content = f'''"""
{script_name.title()} Script
Auto-generated script for Django Config Toolkit.
"""

import os
import sys
from pathlib import Path
from django.core.management import execute_from_command_line
from django.conf import settings

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Import Django
import django
django.setup()

# Import ConfigToolkit
from django_cfg import ConfigToolkit


def main():
    """Main function for {script_name} script."""
    print(f"🚀 Running {script_name} script...")
    
    # Initialize configuration
    config = ConfigToolkit()
    
    # Your script logic here
    print("✅ Script completed successfully!")


if __name__ == '__main__':
    main()
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.stdout.write(f'  📄 Python script created: {script_path}')
        self.stdout.write('  💡 Edit the script to add your custom logic')

    def create_shell_script(self, script_name):
        """Create shell script template"""
        # Create scripts directory
        scripts_dir = Path('scripts')
        scripts_dir.mkdir(exist_ok=True)
        
        # Create script file
        script_path = scripts_dir / f'{script_name}.sh'
        
        script_content = f'''#!/bin/bash

# {script_name.title()} Script
# Auto-generated shell script for Django Config Toolkit.

set -e  # Exit on error

echo "🚀 Running {script_name} script..."

# Your shell script logic here
echo "✅ Script completed successfully!"
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        script_path.chmod(0o755)
        
        self.stdout.write(f'  📄 Shell script created: {script_path}')
        self.stdout.write('  💡 Edit the script to add your custom logic')

    def create_django_command(self, command_name):
        """Create Django management command template"""
        # Create management commands directory
        commands_dir = Path('management/commands')
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        (commands_dir.parent / '__init__.py').touch()
        (commands_dir / '__init__.py').touch()
        
        # Create command file
        command_path = commands_dir / f'{command_name}.py'
        
        command_content = f'''"""
{command_name.title()} Command
Auto-generated Django management command.
"""

from django.core.management.base import BaseCommand
from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = '{command_name.title()} command description'

    def add_arguments(self, parser):
        # Add command arguments here
        pass

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write(self.style.SUCCESS(f'🚀 Running {command_name} command...'))
        
        # Initialize configuration
        config = ConfigToolkit()
        
        # Your command logic here
        self.stdout.write(self.style.SUCCESS('✅ Command completed successfully!'))
'''
        
        with open(command_path, 'w') as f:
            f.write(command_content)
        
        self.stdout.write(f'  📄 Django command created: {command_path}')
        self.stdout.write('  💡 Run with: python manage.py {command_name}')

    def run_script_interactive(self):
        """Run script interactively"""
        self.stdout.write(self.style.SUCCESS('▶️  Run Script\n'))
        
        # List available scripts
        scripts_dir = Path('scripts')
        if not scripts_dir.exists():
            self.stdout.write('❌ No scripts directory found')
            return
        
        # Get available scripts
        python_scripts = [s.stem for s in scripts_dir.glob('*.py') if s.name != '__init__.py']
        shell_scripts = [s.stem for s in scripts_dir.glob('*.sh')]
        
        if not python_scripts and not shell_scripts:
            self.stdout.write('❌ No scripts found')
            return
        
        # Create choices
        choices = []
        if python_scripts:
            choices.append(questionary.Choice('🐍 Python Scripts', value='python'))
        if shell_scripts:
            choices.append(questionary.Choice('🐚 Shell Scripts', value='shell'))
        
        script_type = questionary.select('Script type:', choices=choices).ask()
        
        if script_type == 'python':
            script_name = questionary.select('Select script:', choices=python_scripts).ask()
            self.run_python_script(script_name)
        elif script_type == 'shell':
            script_name = questionary.select('Select script:', choices=shell_scripts).ask()
            self.run_shell_script(script_name)

    def run_script(self, script_name):
        """Run specific script"""
        script_path = Path('scripts') / f'{script_name}.py'
        shell_script_path = Path('scripts') / f'{script_name}.sh'
        
        if script_path.exists():
            self.run_python_script(script_name)
        elif shell_script_path.exists():
            self.run_shell_script(script_name)
        else:
            self.stdout.write(self.style.ERROR(f'❌ Script {script_name} not found'))

    def run_python_script(self, script_name):
        """Run Python script"""
        script_path = Path('scripts') / f'{script_name}.py'
        
        if not script_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Script {script_name} not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Running Python script: {script_name}'))
        
        try:
            # Run script in Django context
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.stdout:
                self.stdout.write(result.stdout)
            if result.stderr:
                self.stdout.write(self.style.WARNING(result.stderr))
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('✅ Script completed successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Script failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error running script: {e}'))

    def run_shell_script(self, script_name):
        """Run shell script"""
        script_path = Path('scripts') / f'{script_name}.sh'
        
        if not script_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Script {script_name} not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Running shell script: {script_name}'))
        
        try:
            result = subprocess.run([
                'bash', str(script_path)
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.stdout:
                self.stdout.write(result.stdout)
            if result.stderr:
                self.stdout.write(self.style.WARNING(result.stderr))
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('✅ Script completed successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Script failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error running script: {e}'))

    def open_django_shell(self):
        """Open Django shell"""
        self.stdout.write(self.style.SUCCESS('🐚 Opening Django Shell...'))
        
        try:
            call_command('shell')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error opening Django shell: {e}'))

    def run_django_check(self):
        """Run Django system check"""
        self.stdout.write(self.style.SUCCESS('🔍 Running Django System Check...'))
        
        try:
            call_command('check', verbosity=2)
            self.stdout.write(self.style.SUCCESS('✅ System check completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ System check failed: {e}'))

    def clean_project(self):
        """Clean project files"""
        self.stdout.write(self.style.SUCCESS('🧹 Cleaning Project...'))
        
        # Files to clean
        files_to_clean = [
            '*.pyc',
            '__pycache__',
            '.pytest_cache',
            '*.log',
            '*.sqlite3',
            'media/',
            'staticfiles/',
        ]
        
        for pattern in files_to_clean:
            if '*' in pattern:
                # Handle glob patterns
                for file_path in Path('.').glob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        self.stdout.write(f'  🗑️  Deleted: {file_path}')
            else:
                # Handle directories
                dir_path = Path(pattern)
                if dir_path.exists() and dir_path.is_dir():
                    import shutil
                    shutil.rmtree(dir_path)
                    self.stdout.write(f'  🗑️  Deleted directory: {dir_path}')
        
        self.stdout.write(self.style.SUCCESS('✅ Project cleaned'))

    def show_project_info(self):
        """Show project information"""
        self.stdout.write(self.style.SUCCESS('📊 Project Information\n'))
        
        # Django version
        import django
        self.stdout.write(f'🐍 Python: {sys.version}')
        self.stdout.write(f'🎯 Django: {django.get_version()}')
        
        # Project settings
        self.stdout.write(f'📁 Project: {settings.SETTINGS_MODULE}')
        self.stdout.write(f'🔧 Debug: {settings.DEBUG}')
        self.stdout.write(f'🌐 Allowed Hosts: {settings.ALLOWED_HOSTS}')
        
        # Installed apps count
        self.stdout.write(f'📦 Installed Apps: {len(settings.INSTALLED_APPS)}')
        
        # Database info
        if hasattr(settings, 'DATABASES'):
            self.stdout.write(f'🗄️  Databases: {len(settings.DATABASES)}')
            for db_name in settings.DATABASES:
                engine = settings.DATABASES[db_name].get('ENGINE', 'Unknown')
                self.stdout.write(f'   - {db_name}: {engine}')
        
        # ConfigToolkit info
        try:
            config = ConfigToolkit()
            self.stdout.write(f'⚙️  ConfigToolkit: Loaded successfully')
        except Exception as e:
            self.stdout.write(f'❌ ConfigToolkit: Error - {e}')
