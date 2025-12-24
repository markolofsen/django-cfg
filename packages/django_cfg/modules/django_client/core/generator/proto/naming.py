"""
Proto Naming Utilities.

Centralized name sanitization and conversion for proto file generation.
"""

import re


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


def sanitize_enum_value(value: str, enum_name: str) -> str:
    """
    Sanitize and format an enum value for proto.

    Proto enum values must be UPPER_SNAKE_CASE and typically prefixed with enum name.

    Examples:
        >>> sanitize_enum_value("device_code", "GrantType")
        'GRANTTYPE_DEVICE_CODE'
        >>> sanitize_enum_value("urn:ietf:params:oauth:grant_type:device_code", "GrantType")
        'GRANTTYPE_URN_IETF_PARAMS_OAUTH_GRANT_TYPE_DEVICE_CODE'
    """
    # First sanitize the value
    sanitized = sanitize_proto_name(str(value)).upper()

    # Add enum name prefix if not already present
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
