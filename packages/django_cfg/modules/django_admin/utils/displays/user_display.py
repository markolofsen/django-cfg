"""User display utilities."""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ...models.display_models import UserDisplayConfig

logger = logging.getLogger(__name__)


class UserDisplay:
    """User display utilities."""

    @classmethod
    def with_avatar(cls, user: Any, config: Optional[UserDisplayConfig] = None) -> List[str]:
        """Display user with avatar for @display(header=True)."""
        config = config or UserDisplayConfig()

        if not user:
            return ["No user", "", "", {}]

        name = getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'username', 'Unknown')
        email = getattr(user, 'email', '') if config.show_email else ''

        name_parts = name.split()
        if len(name_parts) >= 2:
            initials = f"{name_parts[0][0]}{name_parts[1][0]}".upper()
        elif name:
            initials = name[0].upper()
        else:
            initials = "U"

        avatar_data = {"size": config.avatar_size, "initials": initials, "show": config.show_avatar}
        return [name, email, initials, avatar_data]

    @classmethod
    def simple(cls, user: Any, config: Optional[UserDisplayConfig] = None) -> SafeString:
        """Simple user display."""
        config = config or UserDisplayConfig()

        if not user:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">No user</span>')

        name = getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'username', 'Unknown')
        html = format_html('<span class="font-medium">{}</span>', escape(name))

        if config.show_email:
            email = getattr(user, 'email', '')
            if email:
                html = format_html(
                    '{}<br><span class="text-xs text-font-subtle-light dark:text-font-subtle-dark">{}</span>',
                    html, escape(email),
                )

        return html
