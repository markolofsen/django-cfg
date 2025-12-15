"""
Configuration utilities for Web Push integration.
"""


def check_webpush_dependencies(raise_on_missing: bool = False) -> bool:
    """
    Check if webpush dependencies are installed.

    Args:
        raise_on_missing: If True, raise exception when dependencies are missing

    Returns:
        bool: True if all dependencies are available

    Raises:
        ImportError: If raise_on_missing=True and dependencies are missing
    """
    missing = []

    try:
        import pywebpush  # noqa
    except ImportError:
        missing.append("pywebpush")

    if missing:
        message = f"Missing Web Push dependencies: {', '.join(missing)}\nInstall with: pip install pywebpush"
        if raise_on_missing:
            raise ImportError(message)
        return False

    return True


__all__ = ["check_webpush_dependencies"]
