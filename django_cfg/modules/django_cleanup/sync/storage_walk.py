"""Listing a storage by prefix, using only Django's storage API."""

from __future__ import annotations

from typing import Any, Iterator


def walk(storage: Any, prefix: str) -> Iterator[str]:
    """Every file key under `prefix` ("films/12/"), depth first. A missing folder is empty."""
    try:
        dirs, files = storage.listdir(prefix.rstrip("/"))
    except (FileNotFoundError, NotADirectoryError):
        return
    for name in files:
        yield f"{prefix}{name}"
    for name in dirs:
        yield from walk(storage, f"{prefix}{name}/")
