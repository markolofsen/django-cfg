"""
Image token estimation for vision models.

Implements OpenAI's token counting formula for images.
"""

import math
from typing import Literal, Optional, Tuple

# Detail modes
DetailMode = Literal["low", "high", "auto"]

# Token constants (OpenAI formula)
LOW_DETAIL_TOKENS = 85
HIGH_DETAIL_BASE_TOKENS = 85
HIGH_DETAIL_TILE_TOKENS = 170
TILE_SIZE = 512

# Image size limits
MAX_DIMENSION = 2048
SHORT_SIDE_TARGET = 768


def estimate_image_tokens(
    width: int = 1024,
    height: int = 1024,
    detail: DetailMode = "high",
) -> int:
    """
    Estimate tokens for image based on OpenAI formula.

    Low detail: 85 tokens fixed
    High detail: 170 tokens per 512x512 tile + 85 base

    Args:
        width: Image width in pixels
        height: Image height in pixels
        detail: Detail mode (low/high/auto)

    Returns:
        Estimated token count
    """
    # Auto mode: use high for larger images
    if detail == "auto":
        detail = "high" if max(width, height) > 512 else "low"

    if detail == "low":
        return LOW_DETAIL_TOKENS

    # High detail processing
    scaled_width, scaled_height = _scale_image_dimensions(width, height)

    # Count 512x512 tiles
    tiles_x = math.ceil(scaled_width / TILE_SIZE)
    tiles_y = math.ceil(scaled_height / TILE_SIZE)

    return HIGH_DETAIL_BASE_TOKENS + (HIGH_DETAIL_TILE_TOKENS * tiles_x * tiles_y)


def _scale_image_dimensions(width: int, height: int) -> Tuple[int, int]:
    """
    Scale image dimensions according to OpenAI processing rules.

    1. Scale down if larger than 2048 on any side
    2. Scale to fit 768px on shortest side

    Args:
        width: Original width
        height: Original height

    Returns:
        Tuple of (scaled_width, scaled_height)
    """
    # Step 1: Scale down if larger than 2048
    max_dim = max(width, height)
    if max_dim > MAX_DIMENSION:
        scale = MAX_DIMENSION / max_dim
        width = int(width * scale)
        height = int(height * scale)

    # Step 2: Scale to fit 768px on shortest side
    min_dim = min(width, height)
    if min_dim > SHORT_SIDE_TARGET:
        scale = SHORT_SIDE_TARGET / min_dim
        width = int(width * scale)
        height = int(height * scale)

    return width, height


def estimate_cost_from_tokens(
    tokens: int,
    price_per_token: float,
) -> float:
    """
    Calculate cost from token count.

    Args:
        tokens: Number of tokens
        price_per_token: Price per token in USD

    Returns:
        Cost in USD
    """
    return tokens * price_per_token


def get_tile_count(width: int, height: int) -> Tuple[int, int]:
    """
    Get number of 512x512 tiles for image.

    Args:
        width: Image width
        height: Image height

    Returns:
        Tuple of (tiles_x, tiles_y)
    """
    scaled_width, scaled_height = _scale_image_dimensions(width, height)
    tiles_x = math.ceil(scaled_width / TILE_SIZE)
    tiles_y = math.ceil(scaled_height / TILE_SIZE)
    return tiles_x, tiles_y


def get_optimal_detail_mode(
    width: int,
    height: int,
    max_tokens: Optional[int] = None,
) -> DetailMode:
    """
    Determine optimal detail mode based on image size and token budget.

    Args:
        width: Image width
        height: Image height
        max_tokens: Optional maximum token budget for image

    Returns:
        Recommended detail mode
    """
    high_tokens = estimate_image_tokens(width, height, "high")

    # If max_tokens specified and high would exceed it, use low
    if max_tokens and high_tokens > max_tokens:
        return "low"

    # For small images, low detail is sufficient
    if max(width, height) <= 512:
        return "low"

    return "high"


__all__ = [
    "DetailMode",
    "estimate_image_tokens",
    "estimate_cost_from_tokens",
    "get_tile_count",
    "get_optimal_detail_mode",
    "LOW_DETAIL_TOKENS",
    "HIGH_DETAIL_BASE_TOKENS",
    "HIGH_DETAIL_TILE_TOKENS",
]
