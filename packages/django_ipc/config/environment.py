"""
Environment Detection for RPC Configuration

Detects the current environment (development/production/staging/testing)
from environment variables with intelligent fallback logic.
"""

import os
from typing import Literal

# Type-safe environment literal
Environment = Literal["development", "production", "staging", "testing"]


def detect_environment() -> Environment:
    """
    Detect current environment from environment variables.

    Priority order:
    1. DJANGO_ENV environment variable
    2. ENV environment variable
    3. NODE_ENV (for frontend compatibility)
    4. DEBUG flag analysis (True = development, False = production)
    5. Default to 'development'

    Supported aliases:
        - 'dev', 'devel', 'develop', 'local' → 'development'
        - 'prod' → 'production'
        - 'stage' → 'staging'
        - 'test' → 'testing'

    Returns:
        Environment name (development/production/staging/testing)

    Example:
        >>> os.environ['DJANGO_ENV'] = 'prod'
        >>> detect_environment()
        'production'

        >>> os.environ['DJANGO_ENV'] = 'dev'
        >>> detect_environment()
        'development'
    """
    # Try DJANGO_ENV first (primary)
    env = os.getenv("DJANGO_ENV", "").lower().strip()
    if env:
        normalized = _normalize_environment(env)
        if normalized:
            return normalized

    # Try ENV (fallback)
    env = os.getenv("ENV", "").lower().strip()
    if env:
        normalized = _normalize_environment(env)
        if normalized:
            return normalized

    # Try NODE_ENV (for frontend/fullstack apps)
    env = os.getenv("NODE_ENV", "").lower().strip()
    if env:
        normalized = _normalize_environment(env)
        if normalized:
            return normalized

    # Check DEBUG flag as last resort
    debug_value = os.getenv("DEBUG", "").lower().strip()
    if debug_value in ("false", "0", "no", "off"):
        return "production"
    elif debug_value in ("true", "1", "yes", "on"):
        return "development"

    # Default fallback
    return "development"


def _normalize_environment(env: str) -> Environment | None:
    """
    Normalize environment name to standard format.

    Args:
        env: Raw environment name

    Returns:
        Normalized environment name or None if invalid

    Example:
        >>> _normalize_environment('dev')
        'development'

        >>> _normalize_environment('prod')
        'production'

        >>> _normalize_environment('invalid')
        None
    """
    if not env:
        return None

    env_clean = env.lower().strip()

    # Aliases for development
    if env_clean in ("dev", "devel", "develop", "local"):
        return "development"

    # Aliases for production
    if env_clean == "prod":
        return "production"

    # Aliases for staging
    if env_clean == "stage":
        return "staging"

    # Aliases for testing
    if env_clean == "test":
        return "testing"

    # Direct match
    if env_clean in ("development", "production", "staging", "testing"):
        return env_clean  # type: ignore

    # Invalid environment
    return None


def is_development() -> bool:
    """Check if current environment is development."""
    return detect_environment() == "development"


def is_production() -> bool:
    """Check if current environment is production."""
    return detect_environment() == "production"


def is_staging() -> bool:
    """Check if current environment is staging."""
    return detect_environment() == "staging"


def is_testing() -> bool:
    """Check if current environment is testing."""
    return detect_environment() == "testing"


__all__ = [
    "Environment",
    "detect_environment",
    "is_development",
    "is_production",
    "is_staging",
    "is_testing",
]
