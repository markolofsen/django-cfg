"""
Proto Naming Utilities.

Centralized name sanitization and conversion for proto file generation.
"""

import re

# Swift/SwiftUI reserved type names that conflict when used as proto message names
# These will be prefixed with "Proto" when generating Swift code
SWIFT_RESERVED_TYPES = {
    # SwiftUI types
    "Environment",
    "State",
    "Binding",
    "ObservableObject",
    "Published",
    "View",
    "App",
    "Scene",
    # Swift stdlib types
    "Error",
    "Result",
    "Optional",
    "Array",
    "Dictionary",
    "Set",
    "String",
    "Int",
    "Double",
    "Float",
    "Bool",
    "Data",
    "Date",
    "URL",
    "UUID",
    # Common conflicts
    "Type",
    "Self",
    "Protocol",
    "Any",
    "AnyObject",
}


def to_pascal_case(name: str) -> str:
    """
    Convert snake_case or kebab-case to PascalCase.

    Examples:
        >>> to_pascal_case("terminal_streaming_relay")
        'TerminalStreamingRelay'
        >>> to_pascal_case("user-profile")
        'UserProfile'
        >>> to_pascal_case("get_user_by_id")
        'GetUserById'
    """
    words = re.split(r'[-_]', name)
    return ''.join(word.capitalize() for word in words if word)


def to_snake_case(name: str) -> str:
    """
    Convert PascalCase or camelCase to snake_case.

    Examples:
        >>> to_snake_case("UserProfile")
        'user_profile'
        >>> to_snake_case("getAccessToken")
        'get_access_token'
    """
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def sanitize_proto_name(name: str) -> str:
    """
    Sanitize a name for use in proto files.

    Removes or replaces all characters that are not valid in proto identifiers.
    Proto identifiers must start with letter and contain only letters, digits, underscores.

    Examples:
        >>> sanitize_proto_name("user-profile")
        'user_profile'
        >>> sanitize_proto_name("urn:ietf:params:oauth:grant_type:device_code")
        'urn_ietf_params_oauth_grant_type_device_code'
        >>> sanitize_proto_name("some.nested.name")
        'some_nested_name'
    """
    # Replace all non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Clean up multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Strip leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Ensure starts with letter (prefix with underscore if starts with digit)
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    return sanitized


def sanitize_enum_value(value: str, enum_name: str, json_compatible: bool = True) -> str:
    """
    Sanitize and format an enum value for proto.

    Args:
        value: Original enum value from OpenAPI schema
        enum_name: Name of the enum (for prefix if needed)
        json_compatible: If True, preserve original value for JSON serialization.
                        If False, use UPPER_SNAKE_CASE with prefix (proto convention).

    When json_compatible=True (default):
        - Preserves original value for JSON serialization compatibility
        - Only sanitizes invalid proto characters
        - Django/DRF expects original values like "email", "phone"

    When json_compatible=False:
        - Uses UPPER_SNAKE_CASE with enum name prefix (proto convention)
        - Better for pure gRPC usage

    Examples:
        >>> sanitize_enum_value("email", "Channel")  # json_compatible=True
        'email'
        >>> sanitize_enum_value("phone", "Channel")  # json_compatible=True
        'phone'
        >>> sanitize_enum_value("email", "Channel", json_compatible=False)
        'CHANNEL_EMAIL'
    """
    if json_compatible:
        # Preserve original value, only sanitize invalid characters
        sanitized = sanitize_proto_name(str(value))
        # Ensure it's a valid proto identifier (can't start with digit)
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        return sanitized if sanitized else f"{enum_name.lower()}_unknown"
    else:
        # Proto convention: UPPER_SNAKE_CASE with prefix
        sanitized = sanitize_proto_name(str(value)).upper()
        prefix = enum_name.upper()
        if not sanitized.startswith(prefix):
            sanitized = f"{prefix}_{sanitized}"
        return sanitized


def get_message_name(schema_name: str) -> str:
    """
    Get proto message name from schema name.

    Converts schema name to valid proto message name format.

    Examples:
        >>> get_message_name("UserRequest")
        'Userrequest'
        >>> get_message_name("streaming_relay_status")
        'Streamingrelaystatus'
    """
    # Remove special characters and convert
    sanitized = sanitize_proto_name(schema_name)
    # First letter uppercase, rest lowercase (proto convention for messages)
    return sanitized.capitalize() if sanitized else 'Unknown'


def get_field_name(name: str) -> str:
    """
    Get proto field name from property name.

    Proto field names should be lowercase_with_underscores.

    Examples:
        >>> get_field_name("userName")
        'user_name'
        >>> get_field_name("access-token")
        'access_token'
    """
    return to_snake_case(sanitize_proto_name(name))


def get_safe_swift_name(name: str, prefix: str = "Proto") -> str:
    """
    Get a Swift-safe name for proto message/enum.

    If the name conflicts with Swift/SwiftUI reserved types,
    it will be prefixed to avoid compilation errors.

    Args:
        name: The original proto message/enum name
        prefix: Prefix to add for conflicting names (default: "Proto")

    Examples:
        >>> get_safe_swift_name("Environment")
        'ProtoEnvironment'
        >>> get_safe_swift_name("UserProfile")
        'UserProfile'
        >>> get_safe_swift_name("State")
        'ProtoState'
        >>> get_safe_swift_name("Error")
        'ProtoError'
    """
    if name in SWIFT_RESERVED_TYPES:
        return f"{prefix}{name}"
    return name


def is_swift_reserved(name: str) -> bool:
    """
    Check if a name conflicts with Swift/SwiftUI reserved types.

    Examples:
        >>> is_swift_reserved("Environment")
        True
        >>> is_swift_reserved("UserProfile")
        False
    """
    return name in SWIFT_RESERVED_TYPES
