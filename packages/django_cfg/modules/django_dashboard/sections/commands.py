"""Commands section for dashboard."""

from typing import Any, Dict

from .base import DataSection


class CommandsSection(DataSection):
    """
    Management commands section.
    """

    template_name = "admin/sections/commands_section.html"
    title = "Management Commands"
    icon = "terminal"

    def get_data(self) -> Dict[str, Any]:
        """Get commands data."""
        from django_cfg.modules.django_unfold.callbacks.base import (
            get_available_commands,
            get_commands_by_category,
        )

        commands = get_available_commands()
        categorized = get_commands_by_category()

        return {
            'commands': commands,
            'categories': categorized,
            'total_commands': len(commands),
            'core_commands': len([cmd for cmd in commands if cmd.get('is_core')]),
            'custom_commands': len([cmd for cmd in commands if cmd.get('is_custom')]),
        }
