"""
django_rq.capture — RQ job lifecycle capture hooks.

connect_rq_hooks() registers all hooks at Django startup.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_connected: bool = False


def connect_rq_hooks() -> None:
    """Register RQ job lifecycle hooks. Idempotent — safe to call multiple times."""
    global _connected
    if _connected:
        return

    from .hooks import register_hooks
    register_hooks()

    _connected = True
    logger.debug("django_rq: capture hooks connected")


__all__ = ["connect_rq_hooks"]
