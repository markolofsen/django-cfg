"""Typed failures for the asynchronous video generation transport."""

from __future__ import annotations


class VideoGenerationError(RuntimeError):
    """Base error for video generation operations."""


class VideoGenerationHTTPError(VideoGenerationError):
    """A configured video provider rejected an API request."""

    def __init__(
        self,
        *,
        operation: str,
        status_code: int,
        provider: str = "OpenRouter",
        detail: str | None = None,
    ) -> None:
        self.operation = operation
        self.status_code = status_code
        self.provider = provider
        self.detail = detail
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{provider} {operation} failed with HTTP {status_code}{suffix}")


class VideoGenerationFailedError(VideoGenerationError):
    """A previously submitted provider job reached a failed terminal state."""


class VideoGenerationTimeoutError(VideoGenerationError):
    """A bounded wait expired before the provider job became terminal."""


class VideoPricingUnavailableError(VideoGenerationError):
    """The live model capability does not expose an understood pricing SKU."""


class VideoTransportSecurityError(VideoGenerationError):
    """A provider URL violated the HTTPS/origin transport policy."""


__all__ = [
    "VideoGenerationError",
    "VideoGenerationFailedError",
    "VideoGenerationHTTPError",
    "VideoGenerationTimeoutError",
    "VideoPricingUnavailableError",
    "VideoTransportSecurityError",
]
