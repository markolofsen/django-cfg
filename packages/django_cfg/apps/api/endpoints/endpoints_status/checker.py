"""
Endpoints Status Checker

Utility for checking all registered Django URL endpoints.
"""

import re
import time
import uuid
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver
from django.utils import timezone


def get_url_group(url_pattern: str, depth: int = 3) -> str:
    """
    Extract group from URL pattern up to specified depth.

    Examples:
        /api/accounts/profile/ → api/accounts
        /api/payments/webhook/status/ → api/payments/webhook
        /cfg/health/drf/ → cfg/health/drf
        /admin/auth/user/ → admin/auth/user

    Args:
        url_pattern: URL pattern string
        depth: Maximum depth for grouping (default: 3)

    Returns:
        Group name as string
    """
    # Remove leading/trailing slashes and split
    parts = [p for p in url_pattern.strip('/').split('/') if p and '<' not in p]

    # Take up to depth parts
    group_parts = parts[:depth]

    return '/'.join(group_parts) if group_parts else 'root'


def should_check_endpoint(url_pattern: str, url_name: Optional[str] = None) -> bool:
    """
    Determine if endpoint should be checked.

    Excludes:
        - Health check endpoints (to avoid recursion)
        - Admin endpoints
        - Static/media files
        - Django internal endpoints
        - Schema/Swagger/Redoc documentation endpoints
        - DRF format suffix patterns (causes kwarg errors)

    Args:
        url_pattern: URL pattern string
        url_name: Optional URL name

    Returns:
        True if endpoint should be checked
    """
    # Exclude patterns
    exclude_patterns = [
        r'^/?static/',
        r'^/?media/',
        r'^/?admin/',
        r'^/?cfg/health/',  # Exclude health endpoints (recursion prevention)
        r'^/?cfg/api/endpoints/',  # Exclude ourselves
        r'^/__debug__/',
        r'^/__reload__/',
        r'^/?schema/',  # Exclude schema/swagger/redoc documentation endpoints
    ]

    for pattern in exclude_patterns:
        if re.match(pattern, url_pattern):
            return False

    # Exclude DRF format suffix patterns (e.g., \.(?P<format>[a-z0-9]+))
    # These cause "got an unexpected keyword argument 'format'" errors in action methods
    if r'\.(?P<format>' in url_pattern or '<drf_format_suffix:' in url_pattern:
        return False

    # Exclude URL names
    exclude_names = [
        'django_cfg_health',
        'django_cfg_quick_health',
        'django_cfg_drf_health',
        'django_cfg_drf_quick_health',
        'endpoints_status',
        'endpoints_status_drf',
    ]

    if url_name in exclude_names:
        return False

    return True


def get_test_value_for_parameter(param_name: str, param_pattern: str) -> str:
    """
    Generate appropriate test value for URL parameter based on name and pattern.

    Args:
        param_name: Parameter name (e.g., 'slug', 'pk', 'id', 'uuid')
        param_pattern: Regex pattern for the parameter

    Returns:
        Test value string

    Examples:
        slug -> 'test-slug'
        pk -> '1'
        id -> '1'
        uuid -> generated UUID
        format -> 'json'
    """
    param_lower = param_name.lower()

    # UUID parameters
    if 'uuid' in param_lower:
        return str(uuid.uuid4())

    # Primary key / ID parameters
    if param_lower in ['pk', 'id']:
        return '1'

    # Slug parameters
    if 'slug' in param_lower:
        return 'test-slug'

    # Format parameters (for DRF format suffixes)
    if 'format' in param_lower:
        return 'json'

    # Username parameters
    if 'username' in param_lower:
        return 'testuser'

    # Year/Month/Day parameters
    if param_lower == 'year':
        return '2024'
    if param_lower == 'month':
        return '01'
    if param_lower == 'day':
        return '01'

    # Generic string parameter - check pattern
    if '[a-z0-9]' in param_pattern or '[\\w]' in param_pattern:
        return 'test'

    # Numeric parameter
    if '[0-9]' in param_pattern or '\\d' in param_pattern:
        return '1'

    # Default
    return 'test'


def resolve_parametrized_url(url_pattern: str) -> Optional[str]:
    """
    Resolve URL pattern with parameters to concrete URL with test values.

    Supports both regex patterns and Django typed path converters.

    Args:
        url_pattern: URL pattern with Django parameters

    Returns:
        Resolved URL with test values, or None if cannot resolve

    Examples:
        Regex patterns:
        '/api/products/(?P<slug>[^/]+)/' -> '/api/products/test-slug/'
        '/api/users/(?P<pk>[0-9]+)/' -> '/api/users/1/'

        Typed converters:
        '/api/products/<int:pk>/' -> '/api/products/1/'
        '/api/posts/<slug:slug>/' -> '/api/posts/test-slug/'
        '/api/items/<uuid:item_id>/' -> '/api/items/<uuid>/'
    """
    resolved_url = url_pattern

    # First, handle Django typed path converters: <converter:name>
    # Pattern: <type:name>
    typed_converter_regex = r'<([^:>]+):([^>]+)>'

    typed_matches = list(re.finditer(typed_converter_regex, url_pattern))

    for match in typed_matches:
        converter_type = match.group(1)
        param_name = match.group(2)
        full_match = match.group(0)

        # Get test value based on converter type
        if converter_type == 'int':
            test_value = '1'
        elif converter_type == 'slug':
            test_value = 'test-slug'
        elif converter_type == 'uuid':
            test_value = str(uuid.uuid4())
        elif converter_type == 'str':
            test_value = get_test_value_for_parameter(param_name, '')
        elif converter_type == 'path':
            test_value = 'test/path'
        elif converter_type == 'drf_format_suffix':
            test_value = 'json'
        else:
            # Unknown converter - use parameter name to guess
            test_value = get_test_value_for_parameter(param_name, '')

        # Replace typed converter with test value
        resolved_url = resolved_url.replace(full_match, test_value, 1)

    # Then handle regex patterns: (?P<name>pattern)
    param_regex = r'\(\?P<([^>]+)>([^)]+)\)'

    regex_matches = re.finditer(param_regex, resolved_url)

    for match in regex_matches:
        param_name = match.group(1)
        param_pattern = match.group(2)
        full_match = match.group(0)

        # Get test value for this parameter
        test_value = get_test_value_for_parameter(param_name, param_pattern)

        # Replace parameter with test value
        resolved_url = resolved_url.replace(full_match, test_value, 1)

    # Clean up any remaining regex syntax
    resolved_url = re.sub(r'[\^$\\]', '', resolved_url)

    # Check if resolution was successful (no parameter patterns left)
    if '(?P<' in resolved_url or '<' in resolved_url:
        return None

    return resolved_url


def collect_endpoints(
    urlpatterns=None,
    prefix: str = '',
    namespace: str = '',
    include_unnamed: bool = True
) -> List[Dict[str, Any]]:
    """
    Recursively collect all URL endpoints.

    Args:
        urlpatterns: URL patterns to process (default: root resolver)
        prefix: Current URL prefix
        namespace: Current URL namespace
        include_unnamed: Include endpoints without names

    Returns:
        List of endpoint dictionaries
    """
    if urlpatterns is None:
        resolver = get_resolver()
        urlpatterns = resolver.url_patterns

    endpoints = []

    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # This is an include() - recurse
            new_prefix = prefix + str(pattern.pattern)
            new_namespace = namespace

            if hasattr(pattern, 'namespace') and pattern.namespace:
                new_namespace = (
                    f"{namespace}:{pattern.namespace}"
                    if namespace
                    else pattern.namespace
                )

            # Recursively collect nested patterns
            endpoints.extend(
                collect_endpoints(
                    pattern.url_patterns,
                    new_prefix,
                    new_namespace,
                    include_unnamed
                )
            )

        elif isinstance(pattern, URLPattern):
            # Regular URL pattern
            full_pattern = prefix + str(pattern.pattern)

            # Clean up the pattern
            clean_pattern = re.sub(r'\^|\$', '', full_pattern)
            clean_pattern = re.sub(r'\\/', '/', clean_pattern)

            # Ensure leading slash
            if not clean_pattern.startswith('/'):
                clean_pattern = '/' + clean_pattern

            url_name = getattr(pattern, 'name', None)

            # Skip unnamed if requested
            if not include_unnamed and not url_name:
                continue

            # Check if should include this endpoint
            if not should_check_endpoint(clean_pattern, url_name):
                continue

            # Get view info
            view_name = 'unknown'
            if hasattr(pattern, 'callback'):
                callback = pattern.callback
                if hasattr(callback, 'view_class'):
                    view_name = callback.view_class.__name__
                elif hasattr(callback, '__name__'):
                    view_name = callback.__name__

            # Handle patterns with parameters
            if '<' in clean_pattern or '(?P<' in clean_pattern:
                # Try to resolve with test values
                resolved_url = resolve_parametrized_url(clean_pattern)

                if resolved_url:
                    # Successfully resolved - can test it
                    endpoints.append({
                        'url': resolved_url,
                        'url_pattern': clean_pattern,  # Keep original pattern for reference
                        'url_name': url_name,
                        'namespace': namespace,
                        'group': get_url_group(clean_pattern),
                        'view': view_name,
                        'status': 'pending',
                        'has_parameters': True,
                    })
                else:
                    # Cannot resolve - skip
                    endpoints.append({
                        'url': clean_pattern,
                        'url_name': url_name,
                        'namespace': namespace,
                        'group': get_url_group(clean_pattern),
                        'view': view_name,
                        'status': 'skipped',
                        'reason': 'cannot_resolve_parameters',
                    })
            else:
                # No parameters - can test directly
                endpoints.append({
                    'url': clean_pattern,
                    'url_name': url_name,
                    'namespace': namespace,
                    'group': get_url_group(clean_pattern),
                    'view': view_name,
                    'status': 'pending',
                })

    return endpoints


def create_test_user_and_get_token() -> Optional[str]:
    """
    Create test user and generate JWT token.

    Returns:
        JWT access token or None if JWT not available
    """
    try:
        from rest_framework_simplejwt.tokens import RefreshToken

        User = get_user_model()

        # Create or get test user
        username = 'endpoint_test_user'
        email = 'endpoint_test@test.com'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_active': True}
        )

        if created:
            user.set_password('testpass123')
            user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return access_token

    except ImportError:
        # JWT not installed
        return None
    except Exception:
        # Any other error
        return None


def check_endpoint(
    endpoint: Dict[str, Any],
    client: Optional[Client] = None,
    timeout: int = 5,
    auth_token: Optional[str] = None,
    auto_auth: bool = True
) -> tuple[Dict[str, Any], Optional[str]]:
    """
    Check a single endpoint health.

    Automatically creates test user and retries with JWT if endpoint returns 401/403.

    Args:
        endpoint: Endpoint dictionary from collect_endpoints()
        client: Django test client (creates new if None)
        timeout: Request timeout in seconds
        auth_token: JWT token (created automatically on first 401/403)
        auto_auth: Auto-retry with JWT on 401/403 (default: True)

    Returns:
        Tuple of (updated endpoint dictionary, auth_token if created)
    """
    if client is None:
        client = Client()

    # Skip if already marked as skipped
    if endpoint.get('status') == 'skipped':
        return endpoint, auth_token

    url = endpoint['url']
    token_created = False

    try:
        start_time = time.time()

        # First attempt - without auth
        # Add special header to bypass rate limiting for internal checks
        extra_headers = {
            'SERVER_NAME': 'localhost',
            'HTTP_X_DJANGO_CFG_INTERNAL_CHECK': 'true'
        }
        response = client.get(url, timeout=timeout, **extra_headers)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        status_code = response.status_code

        # If unauthorized and auto_auth enabled, retry with token
        requires_auth = False
        if status_code in [401, 403] and auto_auth:
            requires_auth = True

            # Create token if not provided (only once!)
            if auth_token is None:
                auth_token = create_test_user_and_get_token()
                token_created = True

            if auth_token:
                start_time = time.time()
                extra_headers['HTTP_AUTHORIZATION'] = f'Bearer {auth_token}'
                response = client.get(url, timeout=timeout, **extra_headers)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                status_code = response.status_code

        # Determine if healthy
        # 200-299: Success
        # 300-399: Redirects (OK)
        # 401, 403: Auth required (expected, still healthy)
        # 404: Not found (might be OK if endpoint exists but has no data)
        # 405: Method not allowed (endpoint exists, just wrong method)
        # 429: Rate limited (expected for rate-limited APIs, still healthy)
        # 500+: Server errors (unhealthy)

        is_healthy = status_code in [
            200, 201, 204,  # Success
            301, 302, 303, 307, 308,  # Redirects
            401, 403,  # Auth required (expected)
            405,  # Method not allowed (endpoint exists)
            429,  # Rate limited (expected for rate-limited APIs)
        ]

        # Special handling for 404
        reason = None
        if status_code == 404:
            # 404 might be OK for some endpoints (e.g., detail views with no data)
            # Mark as warning rather than unhealthy
            is_healthy = None  # Will be marked as 'warning'
            reason = 'Not Found - endpoint works but no data exists (empty list or test object not found)'

        endpoint.update({
            'status_code': status_code,
            'response_time_ms': round(response_time, 2),
            'is_healthy': is_healthy,
            'status': 'healthy' if is_healthy else ('warning' if is_healthy is None else 'unhealthy'),
            'last_checked': timezone.now().isoformat(),
        })

        if reason:
            endpoint['reason'] = reason

        if requires_auth:
            endpoint['required_auth'] = True

        if status_code == 429:
            endpoint['rate_limited'] = True

    except Exception as e:
        from django.db import DatabaseError, OperationalError

        # Multi-database compatibility: treat DB errors as warnings, not errors
        # Common in multi-database setups with db_constraint=False ForeignKeys
        is_db_error = isinstance(e, (DatabaseError, OperationalError))
        error_message = str(e)[:200]

        # Check for cross-database JOIN errors (common with SQLite multi-db)
        is_cross_db_error = any(keyword in str(e).lower() for keyword in [
            'no such table',
            'no such column',
            'cannot join',
            'cross-database',
            'multi-database'
        ])

        endpoint.update({
            'status_code': None,
            'response_time_ms': None,
            'is_healthy': False if not (is_db_error or is_cross_db_error) else None,
            'status': 'warning' if (is_db_error or is_cross_db_error) else 'error',
            'error': error_message,
            'error_type': 'database' if (is_db_error or is_cross_db_error) else 'general',
            'last_checked': timezone.now().isoformat(),
        })

    # Return endpoint and token (if it was created)
    return endpoint, (auth_token if token_created else None)


def check_all_endpoints(
    include_unnamed: bool = False,
    timeout: int = 5,
    auto_auth: bool = True
) -> Dict[str, Any]:
    """
    Check all registered endpoints.

    Args:
        include_unnamed: Include endpoints without names
        timeout: Request timeout in seconds
        auto_auth: Automatically retry with JWT auth on 401/403 (default: True)

    Returns:
        Dictionary with overall status and all endpoints
    """
    # Collect endpoints
    endpoints = collect_endpoints(include_unnamed=include_unnamed)

    # Create client once
    client = Client()

    # Token will be created lazily on first 401/403
    auth_token = None

    # Check each endpoint
    checked_endpoints = []
    for endpoint in endpoints:
        # Check endpoint (will auto-retry with JWT if needed)
        checked, new_token = check_endpoint(
            endpoint,
            client=client,
            timeout=timeout,
            auth_token=auth_token,
            auto_auth=auto_auth
        )

        # If token was created on first 401/403, save it for ALL subsequent endpoints
        if new_token and auth_token is None:
            auth_token = new_token

        checked_endpoints.append(checked)

    # Calculate statistics
    total = len(checked_endpoints)
    healthy = sum(1 for e in checked_endpoints if e.get('status') == 'healthy')
    unhealthy = sum(1 for e in checked_endpoints if e.get('status') == 'unhealthy')
    warnings = sum(1 for e in checked_endpoints if e.get('status') == 'warning')
    errors = sum(1 for e in checked_endpoints if e.get('status') == 'error')
    skipped = sum(1 for e in checked_endpoints if e.get('status') == 'skipped')

    # Determine overall status
    if errors > 0 or unhealthy > 0:
        overall_status = 'unhealthy'
    elif warnings > 0:
        overall_status = 'degraded'
    else:
        overall_status = 'healthy'

    return {
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'total_endpoints': total,
        'healthy': healthy,
        'unhealthy': unhealthy,
        'warnings': warnings,
        'errors': errors,
        'skipped': skipped,
        'endpoints': checked_endpoints,
    }
