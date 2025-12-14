"""
Django Management Command Base Classes

Ready-to-use base classes for Django management commands with automatic
logger initialization and web execution safety metadata.

Security Integration:
    These classes integrate with django_cfg's security system via:
    - commands_security.py: Analyzes web_executable, requires_input, is_destructive
    - commands_service.py: Filters commands based on safety metadata
    - API views: Blocks unsafe commands from web execution

Available Classes:
    - SafeCommand: Read-only, web-executable commands
    - InteractiveCommand: Commands requiring user input (blocked from web)
    - DestructiveCommand: Commands that modify/delete data (blocked from web)
    - AdminCommand: Administrative commands (safe for web execution)
"""

from django.core.management.base import BaseCommand

from django_cfg.utils import get_logger


class _BaseCommandWithMetadata(BaseCommand):
    """
    Internal base class that adds logger and metadata to commands.

    Do not use directly - use SafeCommand, InteractiveCommand, etc.
    """

    # Default safety metadata (override in subclasses)
    web_executable = False
    requires_input = False
    is_destructive = False

    def __init__(self, *args, **kwargs):
        """Initialize command with automatic logger."""
        super().__init__(*args, **kwargs)

        # Auto-detect command name from module if not set
        if not hasattr(self, 'command_name'):
            self.command_name = self.__module__.split('.')[-1]

        # Initialize logger
        command_name = f"command.{self.command_name}"
        self.logger = get_logger(command_name)

        # Log initialization in debug mode
        # self.logger.debug(
        #     f"Command initialized: {self.command_name} "
        #     f"(web_executable={self.web_executable}, "
        #     f"requires_input={self.requires_input}, "
        #     f"is_destructive={self.is_destructive})"
        # )


class SafeCommand(_BaseCommandWithMetadata):
    """
    Base class for safe, read-only commands that can be executed via web.

    Use this for commands that:
    - Only read data (no modifications)
    - Don't require user input
    - Are safe to run from web interface

    Examples: show_config, list_urls, check_settings

    Usage:
        class Command(SafeCommand):
            help = 'Display current configuration'

            def handle(self, *args, **options):
                self.logger.info("Showing configuration")
                # Read-only operations here

    Metadata:
        web_executable = True
        requires_input = False
        is_destructive = False
    """

    web_executable = True
    requires_input = False
    is_destructive = False


class InteractiveCommand(_BaseCommandWithMetadata):
    """
    Base class for interactive commands requiring user input.

    Use this for commands that:
    - Require input() or questionary prompts
    - Need user interaction
    - Cannot run via web interface

    Examples: superuser, createsuperuser

    Usage:
        class Command(InteractiveCommand):
            help = 'Create superuser with prompts'

            def handle(self, *args, **options):
                self.logger.info("Creating superuser")
                username = input("Username: ")
                # Interactive operations here

    Metadata:
        web_executable = False
        requires_input = True
        is_destructive = False
    """

    web_executable = False
    requires_input = True
    is_destructive = False


class DestructiveCommand(_BaseCommandWithMetadata):
    """
    Base class for destructive commands that modify or delete data.

    Use this for commands that:
    - Delete or modify data
    - Clear caches
    - Perform irreversible operations

    Examples: clear_constance, flush, sqlflush

    Usage:
        class Command(DestructiveCommand):
            help = 'Clear all cache data'

            def handle(self, *args, **options):
                self.logger.warning("Clearing cache - destructive operation")
                # Destructive operations here

    Metadata:
        web_executable = False
        requires_input = True
        is_destructive = True
    """

    web_executable = False
    requires_input = True
    is_destructive = True


class AdminCommand(_BaseCommandWithMetadata):
    """
    Base class for administrative commands safe for web execution.

    Use this for commands that:
    - Perform administrative tasks
    - Are safe despite needing privileges
    - Can be run via web interface

    Examples: migrate, collectstatic, createcachetable

    Usage:
        class Command(AdminCommand):
            help = 'Run database migrations'

            def handle(self, *args, **options):
                self.logger.info("Running migrations")
                # Admin operations here

    Metadata:
        web_executable = True
        requires_input = False
        is_destructive = False
    """

    web_executable = True
    requires_input = False
    is_destructive = False
