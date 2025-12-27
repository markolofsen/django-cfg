"""
Simple naming strategy for TypeScript code generation.

Strategy: Use full operation_id, remove tag prefix, convert to camelCase/PascalCase.
"""



def to_camel_case(s: str) -> str:
    """Convert snake_case, kebab-case, or dot.case to camelCase."""
    # Replace all separators with underscore
    s = s.replace('-', '_').replace('.', '_')
    parts = s.split('_')
    if not parts:
        return ''
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])


def to_pascal_case(s: str) -> str:
    """Convert snake_case, kebab-case, or dot.case to PascalCase."""
    # Replace all separators with underscore
    s = s.replace('-', '_').replace('.', '_')
    return ''.join(p.capitalize() for p in s.split('_'))


def remove_tag_prefix(operation_id: str) -> str:
    """
    Remove common tag prefixes from operation_id.
    
    Examples:
        cfg_newsletter_campaigns_list -> newsletter_campaigns_list
        django_cfg_accounts_login -> accounts_login
        newsletter_campaigns_send_create -> newsletter_campaigns_send_create
    """
    # Remove cfg_ or django_cfg_ prefix
    if operation_id.startswith('django_cfg_'):
        return operation_id[11:]  # len('django_cfg_')
    elif operation_id.startswith('cfg_'):
        return operation_id[4:]   # len('cfg_')
    return operation_id


def operation_to_method_name(
    operation_id: str,
    http_method: str,
    prefix: str,
    base_generator,
    path: str = ''
) -> str:
    """
    Simple naming: remove tag prefix, convert to camelCase/PascalCase.
    
    Args:
        operation_id: Full operation ID from OpenAPI
        http_method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        prefix: Function prefix ('', 'get', 'create', 'use', etc.)
        base_generator: Base generator instance (unused)
        path: URL path (unused)
        
    Returns:
        Method name in camelCase (for client) or PascalCase (for fetchers/hooks)
        
    Examples:
        # Client methods (prefix='')
        cfg_newsletter_campaigns_list -> newsletterCampaignsList
        cfg_newsletter_campaigns_send_create -> newsletterCampaignsSendCreate
        cfg_accounts_otp_request_create -> accountsOtpRequestCreate
        
        # Fetchers (prefix='get')
        cfg_newsletter_campaigns_list -> getNewsletterCampaignsList
        
        # Hooks (prefix='use')
        cfg_newsletter_campaigns_list -> useNewsletterCampaignsList
    """
    # Remove tag prefix
    clean_id = remove_tag_prefix(operation_id)

    # For client methods (no prefix): camelCase
    if not prefix:
        return to_camel_case(clean_id)

    # For fetchers/hooks (with prefix): prefix + PascalCase
    return f"{prefix}{to_pascal_case(clean_id)}"

