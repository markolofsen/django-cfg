"""
Centrifugo channel name validation utilities.

Helps detect common mistakes with channel naming that can lead to permission errors.
"""

import logging
import re
import warnings
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ChannelValidationResult:
    """Result of channel name validation."""

    valid: bool
    warning: Optional[str] = None
    suggestion: Optional[str] = None


def validate_channel_name(channel: str) -> ChannelValidationResult:
    """
    Validate Centrifugo channel name and detect potential issues.

    Common issues:
    - Using `#` for namespace separator (should use `:`)
    - User-limited channels without proper JWT token setup

    Args:
        channel: Channel name to validate

    Returns:
        Validation result with warnings and suggestions

    Examples:
        >>> # ❌ Bad: might be interpreted as user-limited channel
        >>> result = validate_channel_name('terminal#session#abc123')
        >>> print(result.warning)
        Channel "terminal#session#abc123" uses '#' separator...

        >>> # ✅ Good: proper namespace separator
        >>> result = validate_channel_name('terminal:session:abc123')
        >>> print(result.valid)
        True
    """
    # Count # symbols
    hash_count = channel.count("#")

    if hash_count >= 2:
        # Pattern: namespace#something#something
        # This might be interpreted as user-limited channel: namespace#user_id#channel
        parts = channel.split("#")
        namespace, possible_user_id, *rest = parts

        # Check if second part looks like a user ID (numeric)
        is_numeric_user_id = possible_user_id.isdigit()

        if not is_numeric_user_id and possible_user_id:
            # Non-numeric second part after # - likely a mistake
            suggestion = channel.replace("#", ":")

            return ChannelValidationResult(
                valid=False,
                warning=(
                    f'Channel "{channel}" uses \'#\' separator which Centrifugo interprets as '
                    f'user-limited channel boundary. The part "{possible_user_id}" will be treated '
                    f"as user_id, which may cause permission errors if not in JWT token."
                ),
                suggestion=f"Use ':' for namespace separation: \"{suggestion}\"",
            )

        if is_numeric_user_id:
            return ChannelValidationResult(
                valid=True,
                warning=(
                    f'Channel "{channel}" appears to be a user-limited channel '
                    f'(user_id: {possible_user_id}). Make sure your JWT token\'s "sub" '
                    f'field matches "{possible_user_id}".'
                ),
            )

    # Single # is okay for user-limited channels like "user#123"
    if hash_count == 1:
        namespace, user_id_part = channel.split("#")
        if user_id_part and not user_id_part.isdigit() and user_id_part != "*":
            # Non-numeric user_id (not a wildcard) - might be a mistake
            suggestion = channel.replace("#", ":")
            return ChannelValidationResult(
                valid=False,
                warning=(
                    f'Channel "{channel}" uses \'#\' but "{user_id_part}" doesn\'t look '
                    f"like a user_id. This might cause permission issues."
                ),
                suggestion=f"Consider using ':' instead: \"{suggestion}\"",
            )

    return ChannelValidationResult(valid=True)


def log_channel_warnings(channel: str, *, raise_warning: bool = False) -> None:
    """
    Log channel validation warnings (development only).

    Args:
        channel: Channel name to validate
        raise_warning: If True, raises Python warning instead of logging

    Examples:
        >>> # Log to logger
        >>> log_channel_warnings('terminal#session#abc123')

        >>> # Raise Python warning (will be visible in tests)
        >>> log_channel_warnings('terminal#session#abc123', raise_warning=True)
    """
    # Skip in production (if DEBUG=False)
    try:
        from django.conf import settings

        if not settings.DEBUG:
            return
    except (ImportError, AttributeError):
        # Django not configured or DEBUG not set - continue anyway
        pass

    result = validate_channel_name(channel)

    if not result.valid and result.warning:
        message = f"[Centrifugo Channel Warning] {result.warning}"
        if result.suggestion:
            message += f"\n💡 Suggestion: {result.suggestion}"

        if raise_warning:
            warnings.warn(message, UserWarning, stacklevel=2)
        else:
            logger.warning(message)

    elif result.warning:
        # Valid but has informational warning
        if raise_warning:
            warnings.warn(f"[Centrifugo] {result.warning}", UserWarning, stacklevel=2)
        else:
            logger.info(f"[Centrifugo] {result.warning}")


__all__ = [
    "ChannelValidationResult",
    "validate_channel_name",
    "log_channel_warnings",
]
