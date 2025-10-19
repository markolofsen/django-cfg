"""
Management commands collector for django-cfg.

Collects and groups all available Django management commands.
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    from django.apps import apps
    from django.core.management import get_commands
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False


class CommandsCollector:
    """
    Collects and organizes Django management commands by source.
    """

    def __init__(self):
        """Initialize commands collector."""
        self.django_cfg_path = Path(__file__).parent.parent.parent
        self.commands_cache = None

    def get_all_commands(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get all available commands grouped by source.
        
        Returns:
            Dictionary with command groups:
            {
                'django_cfg_core': {'Core Commands': [...]},
                'django_cfg_apps': {'App Name': [...], ...},
                'project_commands': {'Project Commands': [...]}
            }
        """
        if self.commands_cache is not None:
            return self.commands_cache

        commands = {
            'django_cfg_core': {},
            'django_cfg_apps': {},
            'project_commands': {}
        }

        # Get Django-CFG core commands
        core_commands = self._get_django_cfg_core_commands()
        if core_commands:
            commands['django_cfg_core']['Core Commands'] = sorted(core_commands)

        # Get Django-CFG app commands
        app_commands = self._get_django_cfg_app_commands()
        for app_name, app_cmds in app_commands.items():
            if app_cmds:
                commands['django_cfg_apps'][app_name] = sorted(app_cmds)

        # Get project commands (if Django is available)
        if DJANGO_AVAILABLE:
            project_commands = self._get_project_commands()
            if project_commands:
                commands['project_commands']['Project Commands'] = sorted(project_commands)

        self.commands_cache = commands
        return commands

    def _get_django_cfg_core_commands(self) -> List[str]:
        """Get Django-CFG core management commands."""
        commands = []
        core_commands_path = self.django_cfg_path / "management" / "commands"

        if core_commands_path.exists():
            for file_path in core_commands_path.glob("*.py"):
                if file_path.name != "__init__.py":
                    command_name = file_path.stem
                    commands.append(command_name)

        return commands

    def _get_django_cfg_app_commands(self) -> Dict[str, List[str]]:
        """Get Django-CFG app-specific management commands."""
        app_commands = defaultdict(list)
        apps_path = self.django_cfg_path / "apps"

        if not apps_path.exists():
            return dict(app_commands)

        for app_dir in apps_path.iterdir():
            if app_dir.is_dir() and not app_dir.name.startswith('.') and app_dir.name != '__pycache__':
                # Skip @old directory
                if app_dir.name.startswith('@'):
                    continue

                commands_path = app_dir / "management" / "commands"
                if commands_path.exists():
                    app_name = app_dir.name.title()

                    for file_path in commands_path.glob("*.py"):
                        if file_path.name != "__init__.py":
                            command_name = file_path.stem
                            app_commands[app_name].append(command_name)

        return dict(app_commands)

    def _get_project_commands(self) -> List[str]:
        """Get project-specific management commands (excluding Django-CFG)."""
        if not DJANGO_AVAILABLE:
            return []

        try:
            all_commands = get_commands()
            django_cfg_commands = set()

            # Collect all Django-CFG commands
            core_commands = self._get_django_cfg_core_commands()
            django_cfg_commands.update(core_commands)

            app_commands = self._get_django_cfg_app_commands()
            for app_cmds in app_commands.values():
                django_cfg_commands.update(app_cmds)

            # Filter out Django-CFG commands and Django built-ins
            django_builtin_commands = {
                'check', 'compilemessages', 'createcachetable', 'dbshell',
                'diffsettings', 'dumpdata', 'flush', 'inspectdb', 'loaddata',
                'makemessages', 'makemigrations', 'migrate', 'optimizemigration',
                'runserver', 'shell', 'showmigrations', 'sqlflush', 'sqlmigrate',
                'sqlsequencereset', 'squashmigrations', 'startapp', 'startproject',
                'test', 'testserver', 'collectstatic', 'findstatic', 'clearsessions',
                'createsuperuser', 'changepassword'
            }

            project_commands = []
            for cmd_name in all_commands.keys():
                if (cmd_name not in django_cfg_commands and
                    cmd_name not in django_builtin_commands):
                    project_commands.append(cmd_name)

            return project_commands

        except Exception:
            return []

    def get_command_description(self, command_name: str) -> Optional[str]:
        """
        Get command description from its help text.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Command description or None if not available
        """
        if not DJANGO_AVAILABLE:
            return None

        try:
            from django.core.management import load_command_class
            from django.core.management.base import CommandError

            try:
                command = load_command_class(None, command_name)
                return getattr(command, 'help', None) or None
            except (CommandError, ImportError, AttributeError):
                return None
        except Exception:
            return None

    def get_commands_with_descriptions(self) -> Dict[str, Dict[str, Dict[str, Optional[str]]]]:
        """
        Get all commands with their descriptions.
        
        Returns:
            Dictionary with commands and descriptions:
            {
                'django_cfg_core': {'Core Commands': {'cmd': 'description', ...}},
                'django_cfg_apps': {'App Name': {'cmd': 'description', ...}, ...},
                'project_commands': {'Project Commands': {'cmd': 'description', ...}}
            }
        """
        all_commands = self.get_all_commands()
        commands_with_desc = {}

        for category, groups in all_commands.items():
            commands_with_desc[category] = {}

            for group_name, commands in groups.items():
                commands_with_desc[category][group_name] = {}

                for cmd in commands:
                    desc = self.get_command_description(cmd)
                    commands_with_desc[category][group_name][cmd] = desc

        return commands_with_desc


# Global instance
_commands_collector = CommandsCollector()


def get_all_commands() -> Dict[str, Dict[str, List[str]]]:
    """
    Get all available Django management commands grouped by source.
    
    Returns:
        Dictionary with command groups
    """
    return _commands_collector.get_all_commands()


def get_commands_with_descriptions() -> Dict[str, Dict[str, Dict[str, Optional[str]]]]:
    """
    Get all commands with their descriptions.
    
    Returns:
        Dictionary with commands and descriptions
    """
    return _commands_collector.get_commands_with_descriptions()


def get_command_count() -> int:
    """
    Get total count of available commands.
    
    Returns:
        Total number of commands
    """
    all_commands = get_all_commands()
    total = 0

    for category in all_commands.values():
        for commands in category.values():
            total += len(commands)

    return total
