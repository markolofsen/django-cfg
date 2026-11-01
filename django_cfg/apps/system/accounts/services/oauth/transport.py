"""One place that builds the HTTP client for provider calls (finite timeouts; tests patch ``client``)."""

from __future__ import annotations

import httpx

TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT)
