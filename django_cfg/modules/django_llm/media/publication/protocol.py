"""Provider-neutral publication boundary."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import PublishedMedia


@runtime_checkable
class TemporaryMediaPublisher(Protocol):
    def publish(
        self,
        source: bytes | Path,
        *,
        filename: str,
        content_type: str,
        expires_in: timedelta,
        expected_sha256: str | None = None,
    ) -> PublishedMedia: ...

    async def apublish(
        self,
        source: bytes | Path,
        *,
        filename: str,
        content_type: str,
        expires_in: timedelta,
        expected_sha256: str | None = None,
    ) -> PublishedMedia: ...

    def revoke(self, publication: PublishedMedia) -> None: ...

    async def arevoke(self, publication: PublishedMedia) -> None: ...
