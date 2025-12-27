"""
Utility functions for gRPC interceptors.

Contains config loaders and helper methods.
"""

import logging

import grpc.aio

logger = logging.getLogger(__name__)


def get_observability_config():
    """Get observability config from django-cfg or fallback to defaults."""
    try:
        from django_cfg.core import get_current_config
        config = get_current_config()
        if config and hasattr(config, 'grpc') and config.grpc:
            return config.grpc.observability
    except Exception:
        pass
    return None


def is_centrifugo_configured() -> bool:
    """Check if Centrifugo is configured in django-cfg."""
    try:
        from django_cfg.core import get_current_config
        config = get_current_config()
        if config and hasattr(config, 'centrifugo') and config.centrifugo:
            return getattr(config.centrifugo, 'enabled', True)
    except Exception:
        pass
    return False


def extract_peer(metadata) -> str:
    """Extract peer IP from metadata."""
    if metadata:
        for key, value in metadata:
            if key == "x-forwarded-for":
                return value
    return "unknown"


def extract_user_agent(metadata) -> str:
    """Extract user agent from metadata."""
    if metadata:
        metadata_dict = dict(metadata)
        return metadata_dict.get("user-agent", "unknown")
    return "unknown"


def parse_method(full_method: str) -> tuple[str, str]:
    """Parse full method name into service and method."""
    parts = full_method.strip("/").split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return full_method, "unknown"


def extract_ip_from_peer(peer: str) -> str | None:
    """Extract IP address from peer string."""
    try:
        if ":" in peer:
            parts = peer.split(":")
            if len(parts) >= 3 and parts[0] in ["ipv4", "ipv6"]:
                return parts[1]
            elif len(parts) == 2:
                return parts[0]
    except Exception:
        pass
    return None


def get_grpc_code(error: Exception, context: grpc.aio.ServicerContext) -> str:
    """Get gRPC status code from error or context."""
    try:
        if hasattr(error, "code"):
            return error.code().name
        if hasattr(context, "_state") and hasattr(context._state, "code"):
            return context._state.code.name
        return "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def serialize_message(message) -> dict | None:
    """Serialize protobuf message to dict."""
    try:
        from google.protobuf.json_format import MessageToDict
        return MessageToDict(message)
    except Exception:
        return None


__all__ = [
    "get_observability_config",
    "is_centrifugo_configured",
    "extract_peer",
    "extract_user_agent",
    "parse_method",
    "extract_ip_from_peer",
    "get_grpc_code",
    "serialize_message",
]
