"""
Centrifugo Token Generator Service.

Provides utilities for generating Centrifugo JWT tokens with user permissions.
"""

import time
import jwt
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .config_helper import get_centrifugo_config


def get_user_channels(user) -> List[str]:
    """
    Get list of Centrifugo channels user is allowed to subscribe to.

    Args:
        user: Django user instance

    Returns:
        List of channel names user can access

    Channel naming convention:
        - user#{user_id} - Personal channel for RPC responses
        - notifications#user#{user_id} - Personal notifications
        - centrifugo#dashboard - Admin dashboard events
        - admin#notifications - Admin notifications
        - grpc#* - All gRPC bot events (admin only)
        - broadcast - Global broadcast channel
    """
    channels = []

    # Personal channel for RPC responses
    channels.append(f"user#{user.id}")

    # Notifications channel
    channels.append(f"notifications#user#{user.id}")

    # Admin channels
    if user.is_staff or user.is_superuser:
        channels.append("centrifugo#dashboard")
        channels.append("admin#notifications")
        # Allow admins to see all gRPC bot events
        channels.append("grpc#*")

    # Broadcast channel for all users
    channels.append("broadcast")

    return channels


def generate_centrifugo_token(
    user,
    exp_seconds: int = 86400 * 30,  # 30 days
    additional_channels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate Centrifugo JWT token with user's allowed channels.

    Args:
        user: Django user instance
        exp_seconds: Token expiration time in seconds (default: 30 days)
        additional_channels: Optional additional channels to include

    Returns:
        Dictionary with:
            - token: JWT token string
            - centrifugo_url: Centrifugo WebSocket URL
            - expires_at: Token expiration datetime
            - channels: List of allowed channels

    Raises:
        ValueError: If Centrifugo is not configured or disabled
    """
    config = get_centrifugo_config()
    if not config or not config.enabled:
        raise ValueError("Centrifugo not configured or disabled")

    # Get user's allowed channels
    channels = get_user_channels(user)

    # Add additional channels if provided
    if additional_channels:
        channels.extend(additional_channels)
        # Remove duplicates while preserving order
        channels = list(dict.fromkeys(channels))

    # Generate JWT token
    now = int(time.time())
    exp = now + exp_seconds

    payload = {
        "sub": str(user.id),        # User ID
        "exp": exp,                  # Expiration time
        "iat": now,                  # Issued at
        "channels": channels,        # Allowed channels
    }

    # Sign token with HMAC secret
    token = jwt.encode(
        payload,
        config.centrifugo_token_hmac_secret,
        algorithm="HS256"
    )

    # Use timezone-aware datetime for proper ISO 8601 format
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)

    return {
        "token": token,
        "centrifugo_url": config.centrifugo_url,
        "expires_at": expires_at,
        "channels": channels,
    }


__all__ = [
    "get_user_channels",
    "generate_centrifugo_token",
]
