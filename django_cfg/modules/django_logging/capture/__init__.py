"""Capture hooks — wire D1LogHandler into Python logging."""

from __future__ import annotations

import logging

_connected = False


def connect_capture() -> None:
    """Add D1LogHandler to root logger when CloudflareConfig is ready.

    Auto-enables when D1 credentials are configured — no explicit
    DjangoLoggingConfig needed in project config. Can be disabled
    with d1_enabled=False if DjangoLoggingConfig is present.

    Called from AppConfig.ready(). Safe to call multiple times.
    """
    global _connected
    if _connected:
        return
    _connected = True

    try:
        from django_cfg.modules.django_cf import is_ready

        if not is_ready():
            return

        # Check if explicitly disabled via DjangoLoggingConfig
        d1_min_level = "WARNING"
        normalize = True
        try:
            from ..__cfg__ import settings as cfg
            if not cfg.d1_enabled:
                return
            d1_min_level = cfg.d1_min_level
            normalize = cfg.normalization_enabled
        except Exception:
            pass  # no config = auto-enable with defaults

        from ..core.service import LogSyncService
        from .log_handler import D1LogHandler

        service = LogSyncService()
        min_level = getattr(logging, d1_min_level.upper(), logging.WARNING)
        handler = D1LogHandler(
            service,
            min_level=min_level,
            normalize=normalize,
        )
        logging.getLogger().addHandler(handler)
    except Exception:
        pass  # fail silently — file logging continues


__all__ = ["connect_capture"]
