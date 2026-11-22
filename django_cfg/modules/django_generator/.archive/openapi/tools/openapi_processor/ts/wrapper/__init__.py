"""Wrapper generator — per-group `class API` + shared utilities."""

from .generator import (
    GroupSpec,
    WrapperResult,
    discover_group_dirs,
    generate,
)

__all__ = [
    "GroupSpec",
    "WrapperResult",
    "discover_group_dirs",
    "generate",
]
