"""
Image resizing utilities for vision token optimization.

Implements OpenAI's image processing rules to pre-resize images
before sending to API, reducing token costs significantly.

Token costs:
- Low detail: 85 tokens (fixed, image resized to 512x512)
- High detail: 85 base + 170 tokens per 512x512 tile
"""

import logging
from io import BytesIO
from typing import Literal, Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)

# Type alias for detail mode
DetailMode = Literal["low", "high", "auto"]

# OpenAI processing constants (from their documentation)
LOW_DETAIL_SIZE = 512  # Low detail target size
HIGH_DETAIL_SHORT_SIDE = 768  # High detail: scale shortest side to 768
HIGH_DETAIL_MAX_DIM = 2048  # Maximum dimension cap
TILE_SIZE = 512  # Tile size for token calculation


class ImageResizer:
    """
    Resize images for optimal token usage in vision models.

    Implements OpenAI's image processing algorithm:
    1. Low detail: Resize to fit 512x512 (85 tokens)
    2. High detail:
       - Cap at 2048 on longest side
       - Scale shortest side to 768
       - Count 512x512 tiles for tokens

    Example:
        >>> from PIL import Image
        >>> img = Image.open("photo.jpg")
        >>> resized = ImageResizer.resize_image(img, detail="low")
        >>> # Now image fits 512x512, will cost only 85 tokens

        >>> # Or resize bytes directly
        >>> resized_bytes, content_type = ImageResizer.resize_bytes(
        ...     image_bytes, detail="low"
        ... )
    """

    @staticmethod
    def get_optimal_size(
        width: int,
        height: int,
        detail: DetailMode = "low",
    ) -> Tuple[int, int]:
        """
        Calculate optimal resize dimensions based on detail mode.

        Args:
            width: Original width
            height: Original height
            detail: Detail mode (low/high/auto)

        Returns:
            Tuple of (new_width, new_height)
        """
        if detail == "auto":
            # Auto: use low for small images, high for larger
            detail = "low" if max(width, height) <= 512 else "high"

        if detail == "low":
            return ImageResizer._fit_to_box(width, height, LOW_DETAIL_SIZE, LOW_DETAIL_SIZE)

        # High detail processing
        new_w, new_h = width, height

        # Step 1: Cap at 2048 on longest side
        if max(new_w, new_h) > HIGH_DETAIL_MAX_DIM:
            scale = HIGH_DETAIL_MAX_DIM / max(new_w, new_h)
            new_w = int(new_w * scale)
            new_h = int(new_h * scale)

        # Step 2: Scale so shortest side is 768
        if min(new_w, new_h) > HIGH_DETAIL_SHORT_SIDE:
            scale = HIGH_DETAIL_SHORT_SIDE / min(new_w, new_h)
            new_w = int(new_w * scale)
            new_h = int(new_h * scale)

        return new_w, new_h

    @staticmethod
    def resize_image(
        image: Image.Image,
        detail: DetailMode = "low",
        max_dimension: Optional[int] = None,
    ) -> Image.Image:
        """
        Resize PIL image for optimal token usage.

        Args:
            image: PIL Image object
            detail: Detail mode (low/high/auto)
            max_dimension: Optional custom max dimension override

        Returns:
            Resized PIL Image (or original if already small enough)
        """
        width, height = image.size

        if max_dimension:
            new_w, new_h = ImageResizer._fit_to_box(width, height, max_dimension, max_dimension)
        else:
            new_w, new_h = ImageResizer.get_optimal_size(width, height, detail)

        # Skip resize if image is already smaller or equal
        if new_w >= width and new_h >= height:
            logger.debug(f"Image {width}x{height} already optimal, skipping resize")
            return image

        logger.debug(f"Resizing image from {width}x{height} to {new_w}x{new_h} (detail={detail})")

        # Use high-quality LANCZOS resampling
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    @staticmethod
    def resize_bytes(
        image_bytes: bytes,
        detail: DetailMode = "low",
        max_dimension: Optional[int] = None,
        output_format: str = "JPEG",
        quality: int = 85,
    ) -> Tuple[bytes, str]:
        """
        Resize image bytes for optimal token usage.

        Args:
            image_bytes: Raw image bytes
            detail: Detail mode (low/high/auto)
            max_dimension: Optional custom max dimension
            output_format: Output format (JPEG recommended for smaller size)
            quality: JPEG quality (1-100), ignored for other formats

        Returns:
            Tuple of (resized_bytes, content_type)
        """
        image = Image.open(BytesIO(image_bytes))
        original_size = image.size

        # Convert RGBA/P/LA to RGB for JPEG output
        if output_format.upper() == "JPEG" and image.mode in ("RGBA", "P", "LA"):
            if image.mode in ("RGBA", "LA"):
                # Create white background for transparency
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[3])
                else:
                    background.paste(image, mask=image.split()[1])
                image = background
            else:
                image = image.convert("RGB")

        resized = ImageResizer.resize_image(image, detail, max_dimension)

        buffer = BytesIO()
        save_kwargs = {"format": output_format, "optimize": True}
        if output_format.upper() == "JPEG":
            save_kwargs["quality"] = quality

        resized.save(buffer, **save_kwargs)

        content_type = f"image/{output_format.lower()}"
        resized_bytes = buffer.getvalue()

        logger.debug(
            f"Resized image: {original_size} -> {resized.size}, "
            f"{len(image_bytes)} -> {len(resized_bytes)} bytes"
        )

        return resized_bytes, content_type

    @staticmethod
    def estimate_savings(
        original_width: int,
        original_height: int,
        detail: DetailMode = "low",
    ) -> dict:
        """
        Estimate token savings from resizing.

        Args:
            original_width: Original image width
            original_height: Original image height
            detail: Target detail mode

        Returns:
            Dict with original_tokens, resized_tokens, savings info
        """
        from .tokens import estimate_image_tokens

        # Calculate original tokens (assuming high detail for original)
        original_tokens = estimate_image_tokens(original_width, original_height, "high")

        # Calculate resized dimensions and tokens
        new_w, new_h = ImageResizer.get_optimal_size(original_width, original_height, detail)
        target_detail = detail if detail != "auto" else ("low" if max(new_w, new_h) <= 512 else "high")
        resized_tokens = estimate_image_tokens(new_w, new_h, target_detail)

        savings = original_tokens - resized_tokens
        savings_percent = (savings / original_tokens * 100) if original_tokens > 0 else 0

        return {
            "original_size": (original_width, original_height),
            "resized_size": (new_w, new_h),
            "original_tokens": original_tokens,
            "resized_tokens": resized_tokens,
            "tokens_saved": savings,
            "savings_percent": round(savings_percent, 1),
            "detail_mode": target_detail,
        }

    @staticmethod
    def _fit_to_box(
        width: int,
        height: int,
        max_w: int,
        max_h: int,
    ) -> Tuple[int, int]:
        """Scale dimensions to fit within box while preserving aspect ratio."""
        if width <= max_w and height <= max_h:
            return width, height

        ratio = min(max_w / width, max_h / height)
        return int(width * ratio), int(height * ratio)


__all__ = [
    "ImageResizer",
    "DetailMode",
    "LOW_DETAIL_SIZE",
    "HIGH_DETAIL_SHORT_SIDE",
    "HIGH_DETAIL_MAX_DIM",
    "TILE_SIZE",
]
