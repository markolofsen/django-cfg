"""
User Info Tool for MCP.

Allows agents to look up user information by user_id, email, or username.
Automatically uses django_cfg's accounts app (CustomUser model).

This is essential because agents don't have the concept of "current user" —
they receive user identifiers and need to look up user data.
"""

import json
from typing import Any, Dict, Optional

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.services.redactor import apply_redaction, RedactionMode


# Fields that are NEVER returned to agents (even if not in hidden_fields)
HARD_BLOCKED_FIELDS = {
    'password', 'secret_key', 'api_key', 'access_token', 'refresh_token',
    'totp_secret', 'backup_codes', 'session_key',
}


class GetUserInfoTool(MCPTool):
    """
    Look up user information by user_id, email, or username.

    Uses the django_cfg accounts CustomUser model automatically.
    Sensitive fields (passwords, tokens) are always blocked.
    """

    name = "get_user_info"
    description = (
        "Look up user information by user_id, email, or username. "
        "Automatically uses the project's user model. "
        "Sensitive fields like passwords and tokens are never returned."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "User primary key (ID)",
            },
            "email": {
                "type": "string",
                "description": "User email address",
            },
            "username": {
                "type": "string",
                "description": "User username (if using username-based auth)",
            },
        },
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        """Execute the get_user_info tool."""
        try:
            from django.contrib.auth import get_user_model
        except Exception:
            return "Error: Django authentication not available"

        try:
            User = get_user_model()
        except Exception:
            return "Error: User model not available"

        # Build lookup kwargs
        lookup = {}
        if arguments.get("user_id"):
            lookup["pk"] = arguments["user_id"]
        elif arguments.get("email"):
            lookup["email__iexact"] = arguments["email"]
        elif arguments.get("username"):
            lookup["username__iexact"] = arguments["username"]
        else:
            return "Error: Must provide user_id, email, or username"

        try:
            user = User.objects.get(**lookup)
        except User.DoesNotExist:
            return "Error: User not found"
        except User.MultipleObjectsReturned:
            return "Error: Multiple users found (try user_id instead)"
        except Exception as e:
            return f"Error: Lookup failed — {str(e)}"

        # Serialize user data
        user_data = {}
        hidden_fields = self._get_hidden_fields(context)

        for field in User._meta.fields:
            # Always block sensitive fields
            if field.name in HARD_BLOCKED_FIELDS:
                continue

            # Respect MCP config hidden_fields
            if field.name in hidden_fields:
                continue

            value = getattr(user, field.name)

            # Skip sensitive booleans
            if field.name in ('is_staff', 'is_superuser') and not self._is_staff_request(context):
                continue

            # Convert to JSON-safe
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            elif isinstance(value, bytes):
                value = "[binary data]"

            user_data[field.name] = value

        # Apply PII redaction (email, phone, etc.)
        mode = RedactionMode(context.config.redaction.mode.lower())
        user_data = apply_redaction(user_data, mode)

        return json.dumps({
            "found": True,
            "user": user_data,
            "fields_blocked": list(HARD_BLOCKED_FIELDS),
        }, indent=2, default=str)

    def _get_hidden_fields(self, context: Any) -> set:
        """Get hidden fields from MCP config for the User model."""
        try:
            config = context.config
            # Check if 'accounts' or 'system' app is exposed
            for app_label in ('accounts', 'system', 'auth'):
                model_config = config.get_model_config(app_label, 'user')
                if model_config:
                    return set(model_config.hidden_fields)
        except Exception:
            pass
        return set()

    def _is_staff_request(self, context: Any) -> bool:
        """Check if request is from a staff user."""
        user = getattr(context, 'user', None)
        if user and hasattr(user, 'is_staff'):
            return user.is_staff
        return False


# Auto-register when module is imported
get_user_info_tool = GetUserInfoTool()
