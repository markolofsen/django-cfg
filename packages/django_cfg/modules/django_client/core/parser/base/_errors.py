"""
Shared error-collection utility for OpenAPI validation.
"""

from __future__ import annotations


def raise_if_errors(errors: list[str], subject: str) -> None:
    """
    Raise ValueError if any errors were collected.

    Args:
        errors: List of formatted error message strings.
        subject: Short description of what was validated (e.g. "request body").
    """
    if not errors:
        return
    error_list = "".join(errors)
    raise ValueError(
        f"OpenAPI schema has {len(errors)} {subject} bug(s) that would generate incorrect TypeScript hooks."
        f"\n\nFix these issues in Django views before regenerating:"
        f"{error_list}"
        f"\n\nGeneration aborted."
    )
