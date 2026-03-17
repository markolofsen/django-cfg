"""
django_grpc.services.interceptors.event_types — Typed gRPC event payloads.

Replaces raw `**kwargs` dicts that were passed through publish_event() /
publish_error().  Using frozen dataclasses instead of dicts eliminates typos,
enables IDE completion, and lets Pyright catch missing fields at the call site.

Design:
  - Frozen dataclasses (no Pydantic — zero serialisation overhead for internal
    events that never leave the process as-is).
  - Discriminated union via Literal `event_type` field on each subclass.
  - `GrpcEventData` is the base; `GrpcEventPayload` is the tagged union alias.

Usage::

    from .event_types import RpcStartEvent, RpcEndEvent, StreamMessageEvent

    await publisher.publish_event(RpcStartEvent(
        method="/pkg.Service/Method",
        service="Service",
        method_name="Method",
        peer="1.2.3.4",
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GrpcEventData:
    """Common fields present in every gRPC event."""

    method: str
    """Full gRPC method path, e.g. /pkg.MyService/MyMethod."""

    service: str
    """Service name extracted from the path."""

    method_name: str
    """Short method name extracted from the path."""

    peer: str
    """Client IP / peer string from gRPC metadata."""


# ---------------------------------------------------------------------------
# Concrete event types
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class RpcStartEvent(GrpcEventData):
    """Emitted at the start of every RPC call (before the handler runs)."""

    event_type: Literal["rpc_start"] = "rpc_start"


@dataclass(frozen=True, slots=True)
class RpcEndEvent(GrpcEventData):
    """Emitted after a successful RPC call completes."""

    event_type: Literal["rpc_end"] = "rpc_end"
    duration_ms: float = 0.0
    status: str = "OK"
    in_message_count: int = 0
    out_message_count: int = 0


@dataclass(frozen=True, slots=True)
class StreamMessageEvent(GrpcEventData):
    """Emitted per-message in streaming RPCs (client→server or server→client)."""

    event_type: Literal["stream_message"] = "stream_message"
    message_count: int = 0
    direction: Literal["client_to_server", "server_to_client"] = "client_to_server"


@dataclass(frozen=True, slots=True)
class RpcErrorEvent(GrpcEventData):
    """Emitted when a handler raises an exception."""

    event_type: Literal["rpc_error"] = "rpc_error"
    duration_ms: float = 0.0
    status: str = "ERROR"
    in_message_count: int = 0
    out_message_count: int = 0
    error_type: str = ""
    error_message: str = ""


# ---------------------------------------------------------------------------
# Union alias (for type annotations in publisher / interceptor)
# ---------------------------------------------------------------------------

GrpcEventPayload = Union[RpcStartEvent, RpcEndEvent, StreamMessageEvent, RpcErrorEvent]


__all__ = [
    "GrpcEventData",
    "RpcStartEvent",
    "RpcEndEvent",
    "StreamMessageEvent",
    "RpcErrorEvent",
    "GrpcEventPayload",
]
