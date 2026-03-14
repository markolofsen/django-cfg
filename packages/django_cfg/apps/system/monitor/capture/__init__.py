"""
Server-side capture package.

Public API:
    from django_cfg.apps.system.monitor.capture import capture

    capture.exception()          # from within except block
    capture.exception(exc)       # explicit exception
    capture.message("msg", level="warning", extra={...})
"""

from .api import CaptureClient, capture

__all__ = ["CaptureClient", "capture"]
