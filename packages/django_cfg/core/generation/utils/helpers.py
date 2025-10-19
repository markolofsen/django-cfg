"""
Helper utilities for settings generation.

Common functions used across multiple generators.
"""

from typing import Any, Dict


def merge_settings(*settings_dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple settings dictionaries.

    Later dictionaries override earlier ones.

    Args:
        *settings_dicts: Settings dictionaries to merge

    Returns:
        Merged settings dictionary

    Example:
        >>> merge_settings({"A": 1}, {"B": 2}, {"A": 3})
        {"A": 3, "B": 2}
    """
    result = {}
    for settings in settings_dicts:
        result.update(settings)
    return result


__all__ = ["merge_settings"]
