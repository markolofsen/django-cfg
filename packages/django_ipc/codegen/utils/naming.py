"""
Naming utilities for code generation.

Provides functions to convert RPC method names to valid identifiers
in different programming languages.
"""


def sanitize_method_name(name: str) -> str:
    """
    Sanitize method name by replacing dots with underscores.

    This handles namespaced method names (e.g., "workspace.file_changed")
    and converts them to valid identifiers by replacing dots with underscores.

    Args:
        name: Original method name (may contain dots)

    Returns:
        Sanitized name with underscores instead of dots

    Examples:
        >>> sanitize_method_name("workspace.file_changed")
        'workspace_file_changed'
        >>> sanitize_method_name("send_email")
        'send_email'
    """
    return name.replace('.', '_')


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format

    Examples:
        >>> to_camel_case("workspace_file_changed")
        'workspaceFileChanged'
        >>> to_camel_case("send_email")
        'sendEmail'
        >>> to_camel_case("user_update_profile")
        'userUpdateProfile'
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_typescript_method_name(rpc_name: str) -> str:
    """
    Convert RPC method name to valid TypeScript method name.

    Handles namespaced methods by replacing dots with underscores,
    then converts to camelCase.

    Args:
        rpc_name: Original RPC method name (may contain dots)

    Returns:
        Valid TypeScript method name in camelCase

    Examples:
        >>> to_typescript_method_name("workspace.file_changed")
        'workspaceFileChanged'
        >>> to_typescript_method_name("session.message")
        'sessionMessage'
        >>> to_typescript_method_name("send_email")
        'sendEmail'
    """
    sanitized = sanitize_method_name(rpc_name)
    return to_camel_case(sanitized)


def to_python_method_name(rpc_name: str) -> str:
    """
    Convert RPC method name to valid Python method name.

    Handles namespaced methods by replacing dots with underscores.
    Python uses snake_case, so we just sanitize the name.

    Args:
        rpc_name: Original RPC method name (may contain dots)

    Returns:
        Valid Python method name in snake_case

    Examples:
        >>> to_python_method_name("workspace.file_changed")
        'workspace_file_changed'
        >>> to_python_method_name("session.message")
        'session_message'
        >>> to_python_method_name("send_email")
        'send_email'
    """
    return sanitize_method_name(rpc_name)


__all__ = [
    'sanitize_method_name',
    'to_camel_case',
    'to_typescript_method_name',
    'to_python_method_name',
]
