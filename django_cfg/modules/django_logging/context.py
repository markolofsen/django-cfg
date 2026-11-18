"""Correlation ids carried in contextvars; no id is invented when an OpenTelemetry span is active."""
from __future__ import annotations

import contextvars
import ipaddress
import re
import uuid
from typing import Dict, Optional

request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("django_cfg_request_id", default=None)
job_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("django_cfg_job_id", default=None)

_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def otel_ids() -> Dict[str, str]:
    """``trace_id`` / ``span_id`` of the active OpenTelemetry span, else {}."""
    try:
        from opentelemetry import trace
    except Exception:
        return {}
    try:
        ctx = trace.get_current_span().get_span_context()
        if ctx.is_valid:
            return {"trace_id": format(ctx.trace_id, "032x"), "span_id": format(ctx.span_id, "016x")}
    except Exception:
        pass
    return {}


def current_ids() -> Dict[str, str]:
    ids: Dict[str, str] = {}
    rid = request_id_var.get()
    if rid:
        ids["request_id"] = rid
    jid = job_id_var.get()
    if jid:
        ids["job_id"] = jid
    ids.update(otel_ids())
    return ids


def is_trusted_proxy(remote_addr: str) -> bool:
    """A private/loopback peer is a reverse proxy in our deployments (Traefik, docker network)."""
    try:
        ip = ipaddress.ip_address(remote_addr)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback


def new_request_id(incoming: Optional[str], remote_addr: str = "", trust_incoming: bool = True) -> Optional[str]:
    """Trusted-proxy ``X-Request-ID`` if well-formed, else a generated id; None if an OTel span is active.

    ``trust_incoming=False`` (Django setting ``DJANGO_CFG_TRUST_REQUEST_ID = False``) never takes the header:
    behind a proxy that forwards the client's own header, a private peer is still an arbitrary client.

    The id is a log label, never an authority: a forged one only mislabels lines.
    """
    if trust_incoming and incoming and _VALID_ID.fullmatch(incoming) and is_trusted_proxy(remote_addr):
        return incoming
    if otel_ids():
        return None
    return uuid.uuid4().hex
