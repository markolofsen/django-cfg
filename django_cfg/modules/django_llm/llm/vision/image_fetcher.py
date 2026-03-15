"""
Image fetching service with validation.

Provides async image downloading with:
- URL validation (scheme, domain whitelist)
- Content-type validation
- Size limits
- Base64 conversion
- Automatic image resizing for token optimization
"""

import base64
import logging
from typing import Optional, Set, Tuple, TYPE_CHECKING, cast
from urllib.parse import urlparse

import httpx

if TYPE_CHECKING:
    from .image_resizer import DetailMode

logger = logging.getLogger(__name__)


class ImageFetchError(Exception):
    """Error during image fetching."""

    def __init__(self, message: str, url: str):
        self.message = message
        self.url = url
        super().__init__(f"{message}: {url}")


# Allowed image content types
ALLOWED_CONTENT_TYPES: Set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}

# Default settings
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_SIZE_MB = 10


class ImageFetcher:
    """
    Fetches images from URLs with validation.

    Features:
    - URL scheme validation (http/https only)
    - Optional domain whitelist
    - Content-type validation
    - Size limits
    - Async support
    - Automatic image resizing for token optimization
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_size_mb: int = DEFAULT_MAX_SIZE_MB,
        allowed_domains: Optional[list[str]] = None,
        user_agent: Optional[str] = None,
        resize: bool = True,
        detail: "DetailMode" = "low",
    ):
        """
        Initialize image fetcher.

        Args:
            timeout: Request timeout in seconds
            max_size_mb: Maximum image size in megabytes
            allowed_domains: Optional list of allowed domains (None = all allowed)
            user_agent: Optional custom User-Agent header
            resize: Whether to auto-resize images for token optimization (default True)
            detail: Default detail mode for resizing (low/high/auto)
        """
        self._timeout = timeout
        self._max_size = max_size_mb * 1024 * 1024
        self._allowed_domains = set(allowed_domains) if allowed_domains else None
        self._user_agent = user_agent or "Django-LLM-Vision/1.0"
        self._resize = resize
        self._detail = detail

    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and allowed.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid and allowed
        """
        try:
            parsed = urlparse(url)

            # Must be http or https
            if parsed.scheme not in ("http", "https"):
                return False

            # Must have a host
            if not parsed.netloc:
                return False

            # Check domain whitelist if configured
            if self._allowed_domains:
                # Extract domain (without port)
                domain = parsed.netloc.split(":")[0]
                if domain not in self._allowed_domains:
                    return False

            return True

        except Exception:
            return False

    def validate_url(self, url: str) -> None:
        """
        Validate URL and raise error if invalid.

        Args:
            url: URL to validate

        Raises:
            ImageFetchError: If URL is invalid
        """
        if not self.is_valid_url(url):
            raise ImageFetchError("Invalid or disallowed URL", url)

    async def fetch(
        self,
        url: str,
        resize: Optional[bool] = None,
        detail: Optional["DetailMode"] = None,
    ) -> Tuple[bytes, str]:
        """
        Fetch image from URL.

        Args:
            url: Image URL
            resize: Override default resize setting (None uses instance default)
            detail: Override default detail mode (None uses instance default)

        Returns:
            Tuple of (image_bytes, content_type)

        Raises:
            ImageFetchError: On fetch failure
        """
        self.validate_url(url)

        # Use instance defaults if not overridden
        should_resize = resize if resize is not None else self._resize
        detail_mode = detail if detail is not None else self._detail

        headers = {"User-Agent": self._user_agent}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()

                # Validate content type
                content_type = response.headers.get("content-type", "").split(";")[0].strip()
                if content_type not in ALLOWED_CONTENT_TYPES:
                    raise ImageFetchError(
                        f"Invalid content type: {content_type}",
                        url,
                    )

                content = response.content

                # Validate size (before resize)
                if len(content) > self._max_size:
                    raise ImageFetchError(
                        f"Image too large: {len(content)} bytes (max {self._max_size})",
                        url,
                    )

                # Resize if enabled
                if should_resize:
                    from .image_resizer import ImageResizer, DetailMode as DM
                    content, content_type = ImageResizer.resize_bytes(
                        content, detail=cast(DM, detail_mode)
                    )

                logger.debug(f"Fetched image: {url} ({len(content)} bytes, {content_type})")
                return content, content_type

        except httpx.HTTPStatusError as e:
            raise ImageFetchError(f"HTTP error {e.response.status_code}", url) from e
        except httpx.TimeoutException as e:
            raise ImageFetchError("Request timeout", url) from e
        except httpx.RequestError as e:
            raise ImageFetchError(f"Request failed: {e}", url) from e

    def fetch_sync(
        self,
        url: str,
        resize: Optional[bool] = None,
        detail: Optional["DetailMode"] = None,
    ) -> Tuple[bytes, str]:
        """
        Synchronous version of fetch().

        Args:
            url: Image URL
            resize: Override default resize setting (None uses instance default)
            detail: Override default detail mode (None uses instance default)

        Returns:
            Tuple of (image_bytes, content_type)
        """
        self.validate_url(url)

        # Use instance defaults if not overridden
        should_resize = resize if resize is not None else self._resize
        detail_mode = detail if detail is not None else self._detail

        headers = {"User-Agent": self._user_agent}

        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if content_type not in ALLOWED_CONTENT_TYPES:
                raise ImageFetchError(f"Invalid content type: {content_type}", url)

            content = response.content
            if len(content) > self._max_size:
                raise ImageFetchError(
                    f"Image too large: {len(content)} bytes",
                    url,
                )

            # Resize if enabled
            if should_resize:
                from .image_resizer import ImageResizer, DetailMode as DM
                content, content_type = ImageResizer.resize_bytes(
                    content, detail=cast(DM, detail_mode)
                )

            return content, content_type

    @staticmethod
    def to_base64_url(image_bytes: bytes, content_type: str) -> str:
        """
        Convert image bytes to data URL.

        Args:
            image_bytes: Raw image bytes
            content_type: MIME type

        Returns:
            Data URL string (data:image/...;base64,...)
        """
        b64 = base64.b64encode(image_bytes).decode()
        return f"data:{content_type};base64,{b64}"

    async def fetch_as_base64_url(
        self,
        url: str,
        resize: Optional[bool] = None,
        detail: Optional["DetailMode"] = None,
    ) -> str:
        """
        Fetch image and convert to base64 data URL.

        Args:
            url: Image URL
            resize: Override default resize setting (None uses instance default)
            detail: Override default detail mode (None uses instance default)

        Returns:
            Base64 data URL
        """
        content, content_type = await self.fetch(url, resize=resize, detail=detail)
        return self.to_base64_url(content, content_type)

    def fetch_as_base64_url_sync(
        self,
        url: str,
        resize: Optional[bool] = None,
        detail: Optional["DetailMode"] = None,
    ) -> str:
        """
        Synchronous version of fetch_as_base64_url().

        Args:
            url: Image URL
            resize: Override default resize setting (None uses instance default)
            detail: Override default detail mode (None uses instance default)

        Returns:
            Base64 data URL
        """
        content, content_type = self.fetch_sync(url, resize=resize, detail=detail)
        return self.to_base64_url(content, content_type)

    @staticmethod
    def detect_format_from_base64(b64_data: str) -> str:
        """
        Detect image format from base64 data.

        Args:
            b64_data: Base64 encoded image data (without data URL prefix)

        Returns:
            Detected MIME type
        """
        # Check magic bytes from first characters
        if b64_data.startswith("/9j/"):
            return "image/jpeg"
        elif b64_data.startswith("iVBOR"):
            return "image/png"
        elif b64_data.startswith("R0lGOD"):
            return "image/gif"
        elif b64_data.startswith("UklGR"):
            return "image/webp"
        elif b64_data.startswith("Qk"):
            return "image/bmp"
        else:
            return "image/jpeg"  # Default fallback

    @staticmethod
    def build_data_url(b64_data: str, content_type: Optional[str] = None) -> str:
        """
        Build data URL from base64 data.

        Auto-detects format if content_type not provided.

        Args:
            b64_data: Base64 encoded image data
            content_type: Optional MIME type

        Returns:
            Data URL string
        """
        if not content_type:
            content_type = ImageFetcher.detect_format_from_base64(b64_data)
        return f"data:{content_type};base64,{b64_data}"


__all__ = [
    "ImageFetcher",
    "ImageFetchError",
    "ALLOWED_CONTENT_TYPES",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_SIZE_MB",
]
