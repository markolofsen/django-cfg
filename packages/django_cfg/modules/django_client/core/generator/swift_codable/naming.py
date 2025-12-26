"""
Swift naming conventions for code generation.

Handles all naming conversions for Swift Codable generator.
"""

import re

# Swift reserved keywords that need backticks or renaming
SWIFT_KEYWORDS = {
    "class", "struct", "enum", "protocol", "extension",
    "func", "var", "let", "import", "return", "if", "else",
    "switch", "case", "default", "for", "while", "repeat",
    "break", "continue", "in", "self", "super", "nil", "true",
    "false", "is", "as", "try", "throw", "throws", "catch",
    "guard", "defer", "where", "type", "operator", "description",
    "init", "deinit", "subscript", "static", "private", "public",
    "internal", "fileprivate", "open", "final", "override",
    "mutating", "nonmutating", "dynamic", "optional", "required",
    "convenience", "lazy", "weak", "unowned", "inout", "some", "any",
}

# Type names that conflict with Swift metatype syntax (foo.Type)
SWIFT_TYPE_CONFLICTS = {"Type", "Protocol", "self", "Self"}


def to_pascal_case(name: str) -> str:
    """
    Convert any case to PascalCase.

    Handles: snake_case, kebab-case, spaces, mixed, already PascalCase.

    Examples:
        >>> to_pascal_case("user_profile")
        'UserProfile'
        >>> to_pascal_case("machine-sharing")
        'MachineSharing'
        >>> to_pascal_case("Machine sharing")
        'MachineSharing'
        >>> to_pascal_case("ai_chat")
        'AiChat'
        >>> to_pascal_case("ActiveTerminalSession")
        'ActiveTerminalSession'
    """
    if not name:
        return ""

    # If already PascalCase (no separators, starts with uppercase), return as-is
    if "_" not in name and "-" not in name and " " not in name and ":" not in name and name[0].isupper():
        return name

    # Normalize: replace all separators with space (including : for URN-style values)
    normalized = name.replace("-", " ").replace("_", " ").replace(":", " ")

    # Split and capitalize first letter of each word (preserve rest)
    parts = normalized.split()
    return "".join(part[0].upper() + part[1:] if part else "" for part in parts)


def to_camel_case(name: str) -> str:
    """
    Convert any case to camelCase.

    Examples:
        >>> to_camel_case("user_profile")
        'userProfile'
        >>> to_camel_case("machine-sharing")
        'machineSharing'
    """
    pascal = to_pascal_case(name)
    if not pascal:
        return ""
    return pascal[0].lower() + pascal[1:]


def swift_property_name(name: str) -> str:
    """
    Convert property name to Swift camelCase, escaping keywords.

    Examples:
        >>> swift_property_name("user_id")
        'userId'
        >>> swift_property_name("type")
        '`type`'
        >>> swift_property_name("description")
        '`description`'
    """
    camel = to_camel_case(name)
    if camel in SWIFT_KEYWORDS:
        return f"`{camel}`"
    return camel


def sanitize_swift_identifier(name: str) -> str:
    """
    Sanitize string to valid Swift identifier.

    Examples:
        >>> sanitize_swift_identifier("user-profile")
        'UserProfile'
        >>> sanitize_swift_identifier("2users")
        'N2users'
    """
    # Remove invalid characters (keep only alphanumeric and underscores)
    clean = re.sub(r'[^a-zA-Z0-9_ -]', '', name)

    # Convert to PascalCase
    result = to_pascal_case(clean)

    # If starts with digit, prefix with 'N'
    if result and result[0].isdigit():
        result = f'N{result}'

    return result or 'Unknown'
