"""
Django commands callbacks.
"""

import logging
from typing import Dict, Any

from .base import get_available_commands, get_commands_by_category

logger = logging.getLogger(__name__)


class CommandsCallbacks:
    """Django commands callbacks."""
    
    def get_django_commands(self) -> Dict[str, Any]:
        """Get Django management commands information."""
        try:
            commands = get_available_commands()
            categorized = get_commands_by_category()

            return {
                "commands": commands,
                "categorized": categorized,
                "total_commands": len(commands),
                "categories": list(categorized.keys()),
                "core_commands": len([cmd for cmd in commands if cmd['is_core']]),
                "custom_commands": len([cmd for cmd in commands if cmd['is_custom']]),
            }
        except Exception as e:
            logger.error(f"Error getting Django commands: {e}")
            # Return safe fallback to prevent dashboard from breaking
            return {
                "commands": [],
                "categorized": {},
                "total_commands": 0,
                "categories": [],
                "core_commands": 0,
                "custom_commands": 0,
            }
