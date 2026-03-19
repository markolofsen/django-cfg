"""Message normalization and SHA-256 fingerprinting."""

from __future__ import annotations

import hashlib
import re

# Order matters — UUIDs before generic numbers
_PATTERNS = [
    # UUIDs: 8-4-4-4-12 hex
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I), "{uuid}"),
    # IPv4 addresses
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "{ip}"),
    # ISO timestamps (2025-03-19T12:34:56...)
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*"), "{ts}"),
    # Hex hashes (16+ hex chars)
    (re.compile(r"\b[0-9a-f]{16,}\b", re.I), "{hex}"),
    # Standalone numbers (not part of words)
    (re.compile(r"(?<![a-zA-Z_])\d+(?:\.\d+)?(?![a-zA-Z_])"), "{n}"),
]


def normalize_message(message: str) -> str:
    """Strip dynamic data (UUIDs, IPs, timestamps, numbers) from a log message."""
    for pattern, replacement in _PATTERNS:
        message = pattern.sub(replacement, message)
    return message.strip()


def make_fingerprint(
    level: str,
    logger_name: str,
    message: str,
    *,
    normalize: bool = True,
) -> str:
    """SHA-256 fingerprint (first 16 chars) from level + logger + normalized message."""
    if normalize:
        message = normalize_message(message)
    raw = f"{level}:{logger_name}:{message}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


__all__ = ["normalize_message", "make_fingerprint"]
