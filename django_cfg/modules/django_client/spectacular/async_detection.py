"""
Async View Detection for OpenAPI Schema.

Postprocessing hook that detects async-capable Django views and marks
operations with x-async-capable extension for dual client generation.
"""

import inspect
import logging
from typing import Any, Dict, Optional

from django.urls import Resolver404, resolve

logger = logging.getLogger(__name__)


def mark_async_operations(result: Dict[str, Any], generator, request, public) -> Dict[str, Any]:
    """
    DRF Spectacular postprocessing hook to mark async-capable operations.

    Scans Django views and marks operations:
    - async def → operation['x-async-capable'] = True
    - def → operation['x-async-capable'] = False

    Args:
        result: OpenAPI schema dict
        generator: Schema generator instance
        request: HTTP request
        public: Whether schema is public

    Returns:
        Modified OpenAPI schema with async metadata

    Example:
        paths:
          /api/products/:
            get:
              operationId: products_list
              x-async-capable: true  # Async view detected
    """

    if 'paths' not in result:
        return result

    async_count = 0
    sync_count = 0

    for path, methods in result['paths'].items():
        for method, operation in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']:
                # Try to resolve view function
                view_func = _resolve_view_function(path, method, operation)

                if view_func:
                    # Check if view is async
                    is_async = inspect.iscoroutinefunction(view_func)
                    operation['x-async-capable'] = is_async

                    if is_async:
                        async_count += 1
                        logger.debug(f"✓ Async view detected: {method.upper()} {path}")
                    else:
                        sync_count += 1
                else:
                    # Default to sync if cannot resolve
                    operation['x-async-capable'] = False
                    sync_count += 1

    logger.info(f"🔍 Async detection: {async_count} async, {sync_count} sync operations")

    return result


def _resolve_view_function(path: str, method: str, operation: Dict[str, Any]) -> Optional[callable]:
    """
    Resolve view function from OpenAPI operation.

    Args:
        path: API path (e.g., /api/products/)
        method: HTTP method (e.g., GET)
        operation: OpenAPI operation dict

    Returns:
        View function or None if cannot resolve
    """
    # Try to get view from operationId
    operation_id = operation.get('operationId')

    if not operation_id:
        return None

    # Convert path to Django URL format
    # /api/products/{id}/ → /api/products/1/
    django_path = _convert_openapi_path_to_django(path)

    try:
        # Resolve URL to view
        resolved = resolve(django_path)
        view_func = resolved.func

        # Handle ViewSets and class-based views
        if hasattr(view_func, 'cls'):
            # ViewSet - get specific action method
            view_class = view_func.cls

            # Extract action from operationId
            # products_list → list, products_create → create
            action = _extract_action_from_operation_id(operation_id)

            if hasattr(view_class, action):
                return getattr(view_class, action)

            # Fallback to view class itself
            return view_class

        elif hasattr(view_func, 'view_class'):
            # Class-based view
            view_class = view_func.view_class

            # Get method handler (get, post, put, etc.)
            method_lower = method.lower()
            if hasattr(view_class, method_lower):
                return getattr(view_class, method_lower)

            return view_class

        else:
            # Function-based view
            return view_func

    except Resolver404:
        logger.debug(f"Cannot resolve path: {django_path}")
        return None
    except Exception as e:
        logger.debug(f"Error resolving view for {path}: {e}")
        return None


def _convert_openapi_path_to_django(openapi_path: str) -> str:
    """
    Convert OpenAPI path to Django URL format.

    Examples:
        /api/products/{id}/ → /api/products/1/
        /api/posts/{post_slug}/comments/ → /api/posts/test-slug/comments/
    """
    import re

    # Replace path parameters with sample values
    # {id} → 1, {slug} → test-slug, {pk} → 1, {uuid} → sample UUID
    def replace_param(match):
        param_name = match.group(1)

        # Check uuid first (before id, since uuid contains 'id')
        if 'uuid' in param_name.lower():
            return '00000000-0000-0000-0000-000000000001'
        elif 'id' in param_name.lower() or 'pk' in param_name.lower():
            return '1'
        elif 'slug' in param_name.lower():
            return 'test-slug'
        else:
            return 'test-value'

    django_path = re.sub(r'\{([^}]+)\}', replace_param, openapi_path)
    return django_path


def _extract_action_from_operation_id(operation_id: str) -> str:
    """
    Extract ViewSet action from operationId.

    Examples:
        products_list → list
        products_create → create
        products_retrieve → retrieve
        products_partial_update → partial_update
    """
    # Split by underscore and get last part
    parts = operation_id.split('_')

    if len(parts) >= 2:
        # Get everything after first underscore
        # products_list → list
        # products_partial_update → partial_update
        action = '_'.join(parts[1:])
        return action

    return operation_id
