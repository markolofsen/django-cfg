"""
Image encoding utilities for vision models.

Supports automatic image resizing for token optimization.
"""

import base64
import io
import logging
import re
from pathlib import Path
from typing import Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse

import requests
from PIL import Image

if TYPE_CHECKING:
    from .image_resizer import DetailMode

logger = logging.getLogger(__name__)


class ImageEncoder:
    """Utility class for encoding images for vision models."""

    # Supported image formats
    SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "GIF", "WEBP"}

    # Max image size (OpenRouter limit)
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB

    @classmethod
    def encode_from_url(
        cls,
        url: str,
        resize: bool = True,
        detail: "DetailMode" = "low",
        max_dimension: Optional[int] = None,
    ) -> str:
        """
        Download image from URL and encode to base64 data URL.

        Args:
            url: Image URL
            resize: Whether to resize for token optimization
            detail: Detail mode for resizing (low/high/auto)
            max_dimension: Optional max dimension override

        Returns:
            Base64 data URL string
        """
        logger.debug(f"Downloading image from {url}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            content_type = "image/jpeg"

        image_data = response.content

        # Resize if requested
        if resize:
            from .image_resizer import ImageResizer
            image_data, content_type = ImageResizer.resize_bytes(
                image_data,
                detail=detail,
                max_dimension=max_dimension,
            )

        if len(image_data) > cls.MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {len(image_data)} bytes (max {cls.MAX_IMAGE_SIZE})")

        b64_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{content_type};base64,{b64_data}"

    @classmethod
    def encode_from_file(
        cls,
        file_path: str | Path,
        resize: bool = True,
        detail: "DetailMode" = "low",
        max_dimension: Optional[int] = None,
    ) -> str:
        """
        Read image from file and encode to base64 data URL.

        Args:
            file_path: Path to image file
            resize: Whether to resize for token optimization
            detail: Detail mode for resizing (low/high/auto)
            max_dimension: Optional max dimension override

        Returns:
            Base64 data URL string
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        logger.debug(f"Reading image from {file_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        # Determine content type from extension
        ext = path.suffix.lower().lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        content_type = f"image/{ext}"

        # Resize if requested
        if resize:
            from .image_resizer import ImageResizer
            image_data, content_type = ImageResizer.resize_bytes(
                image_data,
                detail=detail,
                max_dimension=max_dimension,
            )

        if len(image_data) > cls.MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {len(image_data)} bytes (max {cls.MAX_IMAGE_SIZE})")

        b64_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{content_type};base64,{b64_data}"

    @classmethod
    def encode_from_bytes(cls, image_bytes: bytes, content_type: str = "image/jpeg") -> str:
        """
        Encode image bytes to base64 data URL.

        Args:
            image_bytes: Raw image bytes
            content_type: MIME type of the image

        Returns:
            Base64 data URL string
        """
        if len(image_bytes) > cls.MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {len(image_bytes)} bytes (max {cls.MAX_IMAGE_SIZE})")

        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{content_type};base64,{b64_data}"

    @classmethod
    def encode_from_pil(cls, image: Image.Image, format: str = "PNG") -> str:
        """
        Encode PIL Image to base64 data URL.

        Args:
            image: PIL Image object
            format: Output format (PNG, JPEG, etc.)

        Returns:
            Base64 data URL string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        image_bytes = buffer.getvalue()

        content_type = f"image/{format.lower()}"
        return cls.encode_from_bytes(image_bytes, content_type)

    @classmethod
    def is_data_url(cls, url: str) -> bool:
        """Check if string is a base64 data URL."""
        return url.startswith("data:image/")

    @classmethod
    def is_http_url(cls, url: str) -> bool:
        """Check if string is an HTTP(S) URL."""
        return url.startswith(("http://", "https://"))

    @classmethod
    def prepare_image_url(
        cls,
        source: str,
        resize: bool = True,
        detail: "DetailMode" = "low",
        max_dimension: Optional[int] = None,
    ) -> str:
        """
        Prepare image URL for vision model.

        Accepts:
        - HTTP(S) URLs (downloaded and encoded if resize=True)
        - Base64 data URLs (resized if resize=True)
        - Local file paths (encoded to base64)

        Args:
            source: Image source (URL, data URL, or file path)
            resize: Whether to resize for token optimization
            detail: Detail mode for resizing (low/high/auto)
            max_dimension: Optional max dimension override

        Returns:
            Image URL ready for vision model
        """
        if cls.is_data_url(source):
            if resize:
                # Decode, resize, re-encode
                return cls._resize_data_url(source, detail, max_dimension)
            return source

        if cls.is_http_url(source):
            if resize:
                # Download, resize, encode
                return cls.encode_from_url(
                    source,
                    resize=True,
                    detail=detail,
                    max_dimension=max_dimension,
                )
            # Return as-is (most models support direct URLs)
            return source

        # Assume it's a file path
        return cls.encode_from_file(
            source,
            resize=resize,
            detail=detail,
            max_dimension=max_dimension,
        )

    @classmethod
    def _resize_data_url(
        cls,
        data_url: str,
        detail: "DetailMode" = "low",
        max_dimension: Optional[int] = None,
    ) -> str:
        """Decode data URL, resize image, and re-encode."""
        import re
        from .image_resizer import ImageResizer

        # Parse data URL
        match = re.match(r"data:([^;,]+)?(?:;base64)?,(.+)", data_url)
        if not match:
            raise ValueError("Invalid data URL format")

        base64_data = match.group(2)
        image_bytes = base64.b64decode(base64_data)

        # Resize
        resized_bytes, content_type = ImageResizer.resize_bytes(
            image_bytes,
            detail=detail,
            max_dimension=max_dimension,
        )

        # Re-encode
        b64_data = base64.b64encode(resized_bytes).decode("utf-8")
        return f"data:{content_type};base64,{b64_data}"

    @classmethod
    def get_image_info(cls, source: str) -> dict:
        """
        Get information about an image.

        Args:
            source: Image source (URL, data URL, or file path)

        Returns:
            Dictionary with image info (width, height, format, size)
        """
        if cls.is_data_url(source):
            # Parse data URL
            match = re.match(r"data:([^;,]+)?(?:;base64)?,(.+)", source)
            if not match:
                raise ValueError("Invalid data URL format")

            mime_type = match.group(1) or "image/png"
            base64_data = match.group(2)
            image_bytes = base64.b64decode(base64_data)

            image = Image.open(io.BytesIO(image_bytes))

        elif cls.is_http_url(source):
            response = requests.get(source, stream=True, timeout=30)
            response.raise_for_status()
            image = Image.open(response.raw)

        else:
            image = Image.open(source)

        return {
            "width": image.size[0],
            "height": image.size[1],
            "format": image.format,
            "mode": image.mode,
        }
