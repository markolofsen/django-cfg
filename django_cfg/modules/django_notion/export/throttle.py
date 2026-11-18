"""Notion allows about 3 requests a second. A 429 is a wait, not a failure."""

from __future__ import annotations

import time
from typing import Callable


class Throttle:
    """One pause before every call, and ``Retry-After`` honoured on a 429 (at most 5 waits per call)."""

    def __init__(self, interval: float = 0.35, sleep: Callable[[float], None] = time.sleep):
        self.interval, self.sleep = interval, sleep

    def call(self, fn, *args, **kwargs):
        for attempt in range(6):
            self.sleep(self.interval)
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                if getattr(exc, "status", None) == 429 and attempt < 5:
                    headers = getattr(exc, "headers", None) or {}
                    try:
                        wait = float(headers.get("retry-after", 5))
                    except (TypeError, ValueError):
                        wait = 5.0
                    self.sleep(max(wait, 1.0))
                    continue
                raise
