"""
Commands Service

Django management commands discovery and documentation.
"""

import logging
from typing import Any, Dict, List

from django.core.management import get_commands, load_command_class

logger = logging.getLogger(__name__)


class CommandsService:
    """
    Service for Django management commands.

    %%PRIORITY:LOW%%
    %%AI_HINT: Discovers available Django management commands%%

    TAGS: commands, django, management, service
    """

    def __init__(self):
        """Initialize commands service."""
        self.logger = logger

    def get_all_commands(self) -> List[Dict[str, Any]]:
        """
        Get all available Django management commands.

        Returns:
            List of command dictionaries with name, app, help text

        %%AI_HINT: Uses Django's get_commands() for command discovery%%
        """
        try:
            commands_dict = get_commands()
            commands_list = []

            for command_name, app_name in commands_dict.items():
                try:
                    # Try to load command to get help text
                    command = load_command_class(app_name, command_name)
                    help_text = getattr(command, 'help', 'No description available')

                    # Determine if it's a core Django command or custom
                    is_core = app_name.startswith('django.')
                    is_custom = not is_core

                    commands_list.append({
                        'name': command_name,
                        'app': app_name,
                        'help': help_text,
                        'is_core': is_core,
                        'is_custom': is_custom,
                    })
                except Exception as e:
                    # If we can't load the command, still include basic info
                    self.logger.debug(f"Could not load command {command_name}: {e}")
                    commands_list.append({
                        'name': command_name,
                        'app': app_name,
                        'help': 'Description unavailable',
                        'is_core': app_name.startswith('django.'),
                        'is_custom': not app_name.startswith('django.'),
                    })

            # Sort by name
            commands_list.sort(key=lambda x: x['name'])
            return commands_list

        except Exception as e:
            self.logger.error(f"Error getting commands: {e}")
            return []

    def get_commands_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get commands organized by category.

        Returns:
            Dictionary with categories as keys and command lists as values

        %%AI_HINT: Categorizes commands by Django core vs custom apps%%
        """
        try:
            all_commands = self.get_all_commands()

            categorized = {
                'Django Core': [],
                'Custom': [],
                'Third Party': [],
            }

            for cmd in all_commands:
                app_name = cmd['app']

                if app_name.startswith('django.'):
                    categorized['Django Core'].append(cmd)
                elif app_name.startswith('django_cfg'):
                    categorized['Custom'].append(cmd)
                else:
                    categorized['Third Party'].append(cmd)

            # Remove empty categories
            return {k: v for k, v in categorized.items() if v}

        except Exception as e:
            self.logger.error(f"Error categorizing commands: {e}")
            return {}

    def get_commands_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about commands.

        Returns:
            Dictionary with total, core, and custom command counts
        """
        try:
            all_commands = self.get_all_commands()
            categorized = self.get_commands_by_category()

            return {
                'total_commands': len(all_commands),
                'core_commands': len([c for c in all_commands if c['is_core']]),
                'custom_commands': len([c for c in all_commands if c['is_custom']]),
                'categories': list(categorized.keys()),
                'commands': all_commands,
                'categorized': categorized,
            }

        except Exception as e:
            self.logger.error(f"Error getting commands summary: {e}")
            return {
                'total_commands': 0,
                'core_commands': 0,
                'custom_commands': 0,
                'categories': [],
                'commands': [],
                'categorized': {},
            }
