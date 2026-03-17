"""
django_grpc.services.interceptors.utils — Interceptor helper functions.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import grpc.aio

logger = logging.getLogger(__name__)


def extract_peer(metadata) -> str:
    """Extract peer IP from invocation metadata."""
    if metadata:
        for key, value in metadata:
            if key == "x-forwarded-for":
                return value
    return "unknown"


def extract_user_agent(metadata) -> str:
    """Extract user-agent from invocation metadata."""
    if metadata:
        metadata_dict = dict(metadata)
        return metadata_dict.get("user-agent", "unknown")
    return "unknown"


def parse_method(full_method: str) -> tuple[str, str]:
    """Parse full method name (e.g. '/pkg.Service/Method') into (service, method)."""
    parts = full_method.strip("/").split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return full_method, "unknown"


def extract_ip_from_peer(peer: str) -> str | None:
    """Extract IP address from gRPC peer string (ipv4:1.2.3.4:port or similar)."""
    try:
        if ":" in peer:
            parts = peer.split(":")
            if len(parts) >= 3 and parts[0] in ("ipv4", "ipv6"):
                return parts[1]
            if len(parts) == 2:
                return parts[0]
    except Exception:
        pass
    return None


def get_grpc_code(error: Exception, context: grpc.aio.ServicerContext) -> str:
    """Get gRPC status code name from error or servicer context."""
    try:
        if hasattr(error, "code"):
            return error.code().name  # type: ignore[union-attr]
        if hasattr(context, "_state") and hasattr(context._state, "code"):
            return context._state.code.name
    except Exception:
        pass
    return "UNKNOWN"


def serialize_message(message) -> dict | None:
    """Serialize protobuf message to dict (best-effort)."""
    try:
        from google.protobuf.json_format import MessageToDict
        return MessageToDict(message)
    except Exception:
        return None


def extract_traceparent(metadata) -> str | None:
    """H-6: Extract W3C traceparent from gRPC invocation metadata.

    gRPC callers that propagate OpenTelemetry traces attach the standard
    ``traceparent`` header (W3C Trace Context spec) as gRPC metadata.
    Extracting it here lets the observability interceptor log / forward the
    trace ID without requiring a full OTel SDK installation.

    Returns the raw ``traceparent`` value (e.g.
    ``"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"``)
    or ``None`` if the header is absent.
    """
    if not metadata:
        return None
    for key, value in metadata:
        if key == "traceparent":
            return value
    return None


def is_centrifugo_configured() -> bool:
    """Check if Centrifugo is enabled in the current django-cfg config."""
    try:
        from django_cfg.core import get_current_config
        config = get_current_config()
        if config and hasattr(config, "centrifugo") and config.centrifugo:
            centrifugo = config.centrifugo
            return bool(centrifugo.enabled if hasattr(centrifugo, "enabled") else False)
    except Exception:
        pass
    return False


__all__ = [
    "extract_peer",
    "extract_user_agent",
    "extract_traceparent",
    "parse_method",
    "extract_ip_from_peer",
    "get_grpc_code",
    "serialize_message",
    "is_centrifugo_configured",
]
