"""
Naming utilities for code generation.

Provides functions to convert RPC method names to valid identifiers
in different programming languages.
"""

# Swift/SwiftUI reserved type names that conflict when used as struct names
# These will be prefixed with "Centrifugo" when generating Swift code
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
    # Common app type conflicts
    "SearchResult",
    "ConnectionState",
}


def get_safe_swift_type_name(name: str, prefix: str = "Centrifugo") -> str:
    """
    Get a Swift-safe type name for a struct/class.

    If the name conflicts with Swift/SwiftUI reserved types,
    it will be prefixed to avoid compilation errors.

    Args:
        name: The original type name
        prefix: Prefix to add for conflicting names (default: "Centrifugo")

    Returns:
        Swift-safe type name

    Examples:
        >>> get_safe_swift_type_name("Environment")
        'CentrifugoEnvironment'
        >>> get_safe_swift_type_name("UserProfile")
        'UserProfile'
        >>> get_safe_swift_type_name("State")
        'CentrifugoState'
    """
    if name in SWIFT_RESERVED_TYPES:
        return f"{prefix}{name}"
    return name


def is_swift_reserved_type(name: str) -> bool:
    """
    Check if a name conflicts with Swift/SwiftUI reserved types.

    Examples:
        >>> is_swift_reserved_type("Environment")
        True
        >>> is_swift_reserved_type("UserProfile")
        False
    """
    return name in SWIFT_RESERVED_TYPES


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


def to_pascal_case(snake_str: str) -> str:
    """
    Convert snake_case to PascalCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in PascalCase format

    Examples:
        >>> to_pascal_case("workspace_file_changed")
        'WorkspaceFileChanged'
        >>> to_pascal_case("send_email")
        'SendEmail'
        >>> to_pascal_case("user_update_profile")
        'UserUpdateProfile'
    """
    return ''.join(word.capitalize() for word in snake_str.split('_'))


def to_go_method_name(rpc_name: str) -> str:
    """
    Convert RPC method name to valid Go method name.

    Handles namespaced methods by replacing dots with underscores,
    then converts to PascalCase (Go exported methods must start with capital).

    Args:
        rpc_name: Original RPC method name (may contain dots)

    Returns:
        Valid Go method name in PascalCase

    Examples:
        >>> to_go_method_name("workspace.file_changed")
        'WorkspaceFileChanged'
        >>> to_go_method_name("session.message")
        'SessionMessage'
        >>> to_go_method_name("send_email")
        'SendEmail'
    """
    sanitized = sanitize_method_name(rpc_name)
    return to_pascal_case(sanitized)


def to_swift_method_name(rpc_name: str) -> str:
    """
    Convert RPC method name to valid Swift method name.

    Handles namespaced methods by replacing dots with underscores,
    then converts to camelCase (Swift convention for methods).

    Args:
        rpc_name: Original RPC method name (may contain dots)

    Returns:
        Valid Swift method name in camelCase

    Examples:
        >>> to_swift_method_name("workspace.file_changed")
        'workspaceFileChanged'
        >>> to_swift_method_name("terminal.input")
        'terminalInput'
        >>> to_swift_method_name("ai_chat.send_message")
        'aiChatSendMessage'
    """
    sanitized = sanitize_method_name(rpc_name)
    return to_camel_case(sanitized)


def to_swift_field_name(field_name: str) -> str:
    """
    Convert field name to valid Swift property name.

    Converts snake_case to camelCase (Swift convention for properties).

    Args:
        field_name: Original field name in snake_case

    Returns:
        Valid Swift property name in camelCase

    Examples:
        >>> to_swift_field_name("user_id")
        'userId'
        >>> to_swift_field_name("session_id")
        'sessionId'
        >>> to_swift_field_name("is_active")
        'isActive'
    """
    return to_camel_case(field_name)


__all__ = [
    'SWIFT_RESERVED_TYPES',
    'get_safe_swift_type_name',
    'is_swift_reserved_type',
    'sanitize_method_name',
    'to_camel_case',
    'to_pascal_case',
    'to_typescript_method_name',
    'to_python_method_name',
    'to_go_method_name',
    'to_swift_method_name',
    'to_swift_field_name',
]
