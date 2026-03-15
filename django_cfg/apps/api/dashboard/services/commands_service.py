"""
Commands Service

Django management commands discovery, documentation, and execution.
"""

import logging
import sys
import time
from io import StringIO
from typing import Any, Dict, Generator, List

from django.core.management import call_command, get_commands, load_command_class

from .commands_security import is_command_allowed, get_command_risk_level

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

    def get_all_commands(self, include_unsafe: bool = False) -> List[Dict[str, Any]]:
        """
        Get all available Django management commands (filtered for safety by default).

        Args:
            include_unsafe: If True, include all commands. If False, only safe commands.

        Returns:
            List of command dictionaries with name, app, help text, safety info

        %%AI_HINT: Uses Django's get_commands() for command discovery with security filtering%%
        """
        try:
            commands_dict = get_commands()
            commands_list = []

            for command_name, app_name in commands_dict.items():
                # Check if command is allowed (unless explicitly including unsafe)
                is_allowed = is_command_allowed(command_name, app_name)

                if not include_unsafe and not is_allowed:
                    continue

                try:
                    # Try to load command to get help text and metadata
                    command = load_command_class(app_name, command_name)
                    help_text = getattr(command, 'help', 'No description available')

                    # Determine if it's a core Django command or custom
                    is_core = app_name.startswith('django.')
                    is_custom = app_name == 'django_cfg'

                    # Get risk level
                    risk_level = get_command_risk_level(command_name, app_name)

                    # Extract security metadata from command instance
                    web_executable = getattr(command, 'web_executable', None)
                    requires_input = getattr(command, 'requires_input', None)
                    is_destructive = getattr(command, 'is_destructive', None)

                    commands_list.append({
                        'name': command_name,
                        'app': app_name,
                        'help': help_text,
                        'is_core': is_core,
                        'is_custom': is_custom,
                        'is_allowed': is_allowed,
                        'risk_level': risk_level,
                        'web_executable': web_executable,
                        'requires_input': requires_input,
                        'is_destructive': is_destructive,
                    })
                except Exception as e:
                    # If we can't load the command, still include basic info
                    self.logger.debug(f"Could not load command {command_name}: {e}")
                    commands_list.append({
                        'name': command_name,
                        'app': app_name,
                        'help': 'Description unavailable',
                        'is_core': app_name.startswith('django.'),
                        'is_custom': app_name == 'django_cfg',
                        'is_allowed': is_allowed,
                        'risk_level': get_command_risk_level(command_name, app_name),
                        'web_executable': None,
                        'requires_input': None,
                        'is_destructive': None,
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
            categorized_dict = self.get_commands_by_category()

            # Convert categorized dict to array of objects
            categorized_array = [
                {
                    'category': category,
                    'commands': commands
                }
                for category, commands in categorized_dict.items()
            ]

            return {
                'total_commands': len(all_commands),
                'core_commands': len([c for c in all_commands if c['is_core']]),
                'custom_commands': len([c for c in all_commands if c['is_custom']]),
                'categories': list(categorized_dict.keys()),
                'commands': all_commands,
                'categorized': categorized_array,
            }

        except Exception as e:
            self.logger.error(f"Error getting commands summary: {e}")
            return {
                'total_commands': 0,
                'core_commands': 0,
                'custom_commands': 0,
                'categories': [],
                'commands': [],
                'categorized': [],
            }

    def get_command_help(self, command_name: str) -> Dict[str, Any]:
        """
        Get detailed help text for a specific command.

        Args:
            command_name: Name of the Django management command

        Returns:
            Dictionary with help text and command info
        """
        try:
            commands_dict = get_commands()

            if command_name not in commands_dict:
                return {
                    'status': 'error',
                    'error': f"Command '{command_name}' not found",
                }

            app_name = commands_dict[command_name]

            # Load command class
            command_class = load_command_class(app_name, command_name)
            command_instance = command_class()

            # Get parser to extract help
            parser = command_instance.create_parser('manage.py', command_name)
            help_text = parser.format_help()

            return {
                'status': 'success',
                'command': command_name,
                'app': app_name,
                'help_text': help_text,
                'is_allowed': is_command_allowed(command_name, app_name),
                'risk_level': get_command_risk_level(command_name, app_name),
            }

        except Exception as e:
            self.logger.error(f"Error getting help for command {command_name}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'command': command_name,
            }

    def execute_command(
        self,
        command_name: str,
        args: List[str] = None,
        options: Dict[str, Any] = None,
        user=None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a Django management command and stream output.

        Args:
            command_name: Name of the command to execute
            args: List of positional arguments
            options: Dictionary of command options
            user: User executing the command (for logging)

        Yields:
            Dict with execution events (start, output, complete, error)

        Security:
            - Validates command is allowed via is_command_allowed()
            - Logs all execution attempts
            - Captures and streams output safely
        """
        args = args or []
        options = options or {}
        start_time = time.time()

        try:
            # Validate command exists
            commands_dict = get_commands()
            if command_name not in commands_dict:
                yield {
                    'type': 'error',
                    'error': f"Command '{command_name}' not found",
                    'available_commands': list(commands_dict.keys())[:20],  # First 20 for reference
                }
                return

            app_name = commands_dict[command_name]

            # Security check - validate command is allowed
            if not is_command_allowed(command_name, app_name):
                self.logger.warning(
                    f"Attempted execution of forbidden command '{command_name}' by user {user}"
                )
                yield {
                    'type': 'error',
                    'error': f"Command '{command_name}' is not allowed via web interface for security reasons",
                    'suggestion': 'Only safe django_cfg commands and whitelisted utilities can be executed via web.',
                    'risk_level': get_command_risk_level(command_name, app_name),
                }
                return

            # Send start event
            yield {
                'type': 'start',
                'command': command_name,
                'args': args,
                'options': options,
            }

            # Capture command output
            output_buffer = StringIO()
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            try:
                # Redirect stdout/stderr to buffer
                sys.stdout = output_buffer
                sys.stderr = output_buffer

                # Execute command
                call_command(command_name, *args, **options)
                return_code = 0

            except Exception as e:
                # Command execution failed
                output_buffer.write(f"\nError: {str(e)}\n")
                return_code = 1

            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            # Get all output
            output = output_buffer.getvalue()

            # Stream output line by line
            if output:
                for line in output.split('\n'):
                    if line.strip():
                        yield {
                            'type': 'output',
                            'line': line,
                        }

            execution_time = time.time() - start_time

            # Send completion event
            yield {
                'type': 'complete',
                'return_code': return_code,
                'execution_time': round(execution_time, 2),
            }

            # Log command execution
            if return_code == 0:
                self.logger.info(
                    f"Command executed: {command_name} {' '.join(args)} "
                    f"by user {user} in {execution_time:.2f}s"
                )
            else:
                self.logger.error(
                    f"Command failed: {command_name} {' '.join(args)} "
                    f"by user {user} in {execution_time:.2f}s"
                )

        except Exception as e:
            execution_time = time.time() - start_time

            self.logger.error(
                f"Command execution error: {command_name} by user {user}: {e}"
            )

            yield {
                'type': 'error',
                'error': str(e),
                'execution_time': round(execution_time, 2),
            }
