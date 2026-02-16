"""
Shared Naming Utilities for Django Client Generator.

Common string transformations used across all generators.

Usage:
    from django_cfg.modules.django_client.core.utils import to_camel_case, to_pascal_case

    to_camel_case("user_profile")  # "userProfile"
    to_pascal_case("user_profile")  # "UserProfile"
    to_snake_case("UserProfile")  # "user_profile"
    header_to_param_name("X-Chunk-Index")  # "xChunkIndex"
"""

from __future__ import annotations

import re


def to_camel_case(name: str) -> str:
    """
    Convert string to camelCase.

    Handles snake_case, kebab-case, and mixed inputs.

    Examples:
        >>> to_camel_case("user_profile")
        'userProfile'
        >>> to_camel_case("machine-sharing")
        'machineSharing'
        >>> to_camel_case("HTTPClient")
        'httpClient'
        >>> to_camel_case("users_list")
        'usersList'
    """
    # Normalize separators
    normalized = name.replace("-", "_")

    # Split on underscores
    parts = normalized.split("_")

    if not parts:
        return name.lower()

    # First part lowercase, rest title case
    result = parts[0].lower()
    for part in parts[1:]:
        if part:
            result += part.capitalize()

    return result


def to_pascal_case(name: str) -> str:
    """
    Convert string to PascalCase.

    Handles snake_case, kebab-case, and mixed inputs.

    Examples:
        >>> to_pascal_case("user_profile")
        'UserProfile'
        >>> to_pascal_case("machine-sharing")
        'MachineSharing'
        >>> to_pascal_case("http_client")
        'HttpClient'
    """
    # Normalize separators
    normalized = name.replace("-", "_")

    # Split on underscores
    parts = normalized.split("_")

    # Capitalize each part
    return "".join(part.capitalize() for part in parts if part)


def to_snake_case(name: str) -> str:
    """
    Convert string to snake_case.

    Handles PascalCase, camelCase, and mixed inputs.

    Examples:
        >>> to_snake_case("UserProfile")
        'user_profile'
        >>> to_snake_case("userProfile")
        'user_profile'
        >>> to_snake_case("HTTPClient")
        'http_client'
    """
    # Insert underscore before uppercase letters (except at start)
    result = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return result.lower()


def header_to_param_name(header_name: str) -> str:
    """
    Convert HTTP header name to camelCase parameter name.

    Handles standard HTTP headers with hyphens.

    Examples:
        >>> header_to_param_name("X-Chunk-Index")
        'xChunkIndex'
        >>> header_to_param_name("Content-Type")
        'contentType'
        >>> header_to_param_name("X-Is-Last")
        'xIsLast'
        >>> header_to_param_name("Authorization")
        'authorization'
    """
    # Remove leading/trailing whitespace and split by hyphen
    parts = header_name.strip().split("-")

    if not parts:
        return header_name.lower()

    # First part lowercase, rest title case
    return parts[0].lower() + "".join(p.title() for p in parts[1:])
