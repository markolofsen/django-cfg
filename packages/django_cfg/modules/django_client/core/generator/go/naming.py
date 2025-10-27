"""
Naming conventions for Go code generation.

Handles conversions between Python/OpenAPI naming and Go naming conventions:
- snake_case → PascalCase (for exports)
- snake_case → camelCase (for unexported)
- Proper Go identifier sanitization
"""

import re


def to_pascal_case(snake_str: str) -> str:
    """
    Convert snake_case to PascalCase.

    Args:
        snake_str: snake_case string

    Returns:
        PascalCase string

    Examples:
        >>> to_pascal_case("user_profile")
        'UserProfile'
        >>> to_pascal_case("api_key_id")
        'APIKeyID'
        >>> to_pascal_case("http_response")
        'HTTPResponse'
    """
    if not snake_str:
        return ""

    # Handle special acronyms that should be uppercase
    acronyms = {'id', 'api', 'http', 'https', 'url', 'uri', 'json', 'xml', 'html', 'css', 'sql', 'uuid'}

    # Split by underscore
    parts = snake_str.split('_')

    # Capitalize each part, with special handling for acronyms
    result_parts = []
    for part in parts:
        if not part:
            continue

        # If entire part is an acronym, uppercase it
        if part.lower() in acronyms:
            result_parts.append(part.upper())
        else:
            # Check if part ends with an acronym
            found_acronym = False
            for acronym in acronyms:
                if part.lower().endswith(acronym):
                    # Split off the acronym
                    prefix = part[:-len(acronym)]
                    if prefix:
                        result_parts.append(prefix.capitalize())
                    result_parts.append(acronym.upper())
                    found_acronym = True
                    break

            if not found_acronym:
                result_parts.append(part.capitalize())

    return ''.join(result_parts)


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to camelCase (unexported).

    Args:
        snake_str: snake_case string

    Returns:
        camelCase string

    Examples:
        >>> to_camel_case("user_profile")
        'userProfile'
        >>> to_camel_case("http_client")
        'httpClient'
    """
    pascal = to_pascal_case(snake_str)
    if not pascal:
        return ""

    # Lowercase the first character
    return pascal[0].lower() + pascal[1:]


def sanitize_go_identifier(name: str) -> str:
    """
    Sanitize string to valid Go identifier.

    Args:
        name: Raw identifier name

    Returns:
        Valid Go identifier

    Examples:
        >>> sanitize_go_identifier("user-profile")
        'UserProfile'
        >>> sanitize_go_identifier("2users")
        'N2users'
        >>> sanitize_go_identifier("class")
        'Class'
    """
    # Replace hyphens with underscores
    name = name.replace('-', '_')

    # Remove invalid characters
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)

    # If starts with digit, prefix with 'N'
    if name and name[0].isdigit():
        name = f'N{name}'

    # Convert to PascalCase
    return to_pascal_case(name) if name else 'Unknown'


def to_snake_case(camel_str: str) -> str:
    """
    Convert PascalCase/camelCase to snake_case.

    Args:
        camel_str: PascalCase or camelCase string

    Returns:
        snake_case string

    Examples:
        >>> to_snake_case("UserProfile")
        'user_profile'
        >>> to_snake_case("APIKey")
        'api_key'
        >>> to_snake_case("HTTPSConnection")
        'https_connection'
    """
    # Insert underscore before uppercase letters (except first)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    # Insert underscore before uppercase letters followed by lowercase
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_go_field_name(field_name: str) -> str:
    """
    Get Go struct field name (exported PascalCase).

    Args:
        field_name: Original field name (snake_case)

    Returns:
        Go field name (PascalCase)

    Examples:
        >>> get_go_field_name("user_id")
        'UserID'
        >>> get_go_field_name("created_at")
        'CreatedAt'
    """
    return to_pascal_case(field_name)


def get_go_package_name(name: str) -> str:
    """
    Get valid Go package name (lowercase, no underscores).

    Args:
        name: Package name

    Returns:
        Valid Go package name

    Examples:
        >>> get_go_package_name("api_client")
        'apiclient'
        >>> get_go_package_name("UserService")
        'userservice'
    """
    # Convert to lowercase
    name = name.lower()

    # Remove invalid characters (keep only letters and digits)
    name = re.sub(r'[^a-z0-9]', '', name)

    # Must not start with digit
    if name and name[0].isdigit():
        name = f'pkg{name}'

    return name or 'client'
