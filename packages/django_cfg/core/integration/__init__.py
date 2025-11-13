"""
Django CFG Integration Package.

Provides URL integration and startup information display.
"""

import os

from .display.ngrok import NgrokDisplayManager
from .display.startup import StartupDisplayManager
from .url_integration import add_django_cfg_urls, get_django_cfg_urls_info

# Module-level flag that persists across hot reloads
_startup_info_shown = False


def print_startup_info():
    """Print startup information based on config.startup_info_mode."""
    global _startup_info_shown

    # Skip if already shown (prevents spam on hot reload)
    if _startup_info_shown:
        return

    # Only show in the actual worker process (not in autoreload parent process)
    # RUN_MAIN is set by Django's autoreloader in the worker process
    if os.environ.get('RUN_MAIN') != 'true':
        return

    # Mark as shown to prevent duplicate display on subsequent hot reloads
    _startup_info_shown = True

    manager = StartupDisplayManager()
    manager.display_startup_info()

def reset_startup_info_flag():
    """Reset the startup info display flag. Useful for testing or manual reset."""
    global _startup_info_shown
    _startup_info_shown = False

def print_ngrok_tunnel_info(tunnel_url: str):
    """Print ngrok tunnel information after tunnel is established."""
    manager = NgrokDisplayManager()
    manager.display_tunnel_info(tunnel_url)

from .commands_collector import get_all_commands, get_command_count, get_commands_with_descriptions
from .version_checker import get_current_version, get_latest_version, get_version_info
from .timing import (
    ServerStartupTimer,
    start_django_timer,
    start_grpc_timer,
    get_django_timer,
    get_grpc_timer,
    get_django_startup_time,
    get_grpc_startup_time,
)

__all__ = [
    "add_django_cfg_urls",
    "get_django_cfg_urls_info",
    "print_startup_info",
    "reset_startup_info_flag",
    "print_ngrok_tunnel_info",
    "get_version_info",
    "get_latest_version",
    "get_current_version",
    "get_all_commands",
    "get_command_count",
    "get_commands_with_descriptions",
    # Timing utilities
    "ServerStartupTimer",
    "start_django_timer",
    "start_grpc_timer",
    "get_django_timer",
    "get_grpc_timer",
    "get_django_startup_time",
    "get_grpc_startup_time",
]
