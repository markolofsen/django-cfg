"""
Django CFG Integration Package.

Provides URL integration and startup information display.
"""

from .url_integration import add_django_cfg_urls, get_django_cfg_urls_info
from .display.startup import StartupDisplayManager
from .display.ngrok import NgrokDisplayManager

def print_startup_info():
    """Print startup information based on config.startup_info_mode."""
    try:
        manager = StartupDisplayManager()
        manager.display_startup_info()
    except Exception as e:
        import traceback
        print(f"❌ ERROR in print_startup_info: {e}")
        print("🔍 TRACEBACK:")
        traceback.print_exc()

def print_ngrok_tunnel_info(tunnel_url: str):
    """Print ngrok tunnel information after tunnel is established."""
    try:
        manager = NgrokDisplayManager()
        manager.display_tunnel_info(tunnel_url)
    except Exception as e:
        import traceback
        print(f"❌ ERROR in print_ngrok_tunnel_info: {e}")
        print("🔍 TRACEBACK:")
        traceback.print_exc()

from .version_checker import get_version_info, get_latest_version, get_current_version
from .commands_collector import get_all_commands, get_command_count, get_commands_with_descriptions

__all__ = [
    "add_django_cfg_urls",
    "get_django_cfg_urls_info", 
    "print_startup_info",
    "print_ngrok_tunnel_info",
    "get_version_info",
    "get_latest_version", 
    "get_current_version",
    "get_all_commands",
    "get_command_count",
    "get_commands_with_descriptions",
]
