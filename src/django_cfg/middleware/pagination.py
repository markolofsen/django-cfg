"""
Django CFG Default Pagination Classes

Provides enhanced pagination classes with better response format and schema support.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from typing import Dict, Any, Optional
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound


class DefaultPagination(PageNumberPagination):
    """
    Enhanced default pagination class for django-cfg projects.
    
    Features:
    - Configurable page size via query parameter
    - Enhanced response format with detailed pagination info
    - Better OpenAPI schema support
    - Consistent error handling
    """
    
    # Page size configuration
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    # Page number configuration
    page_query_param = 'page'
    
    # Template for invalid page messages
    invalid_page_message = 'Invalid page "{page_number}": {message}.'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a page object,
        or `None` if pagination is not configured for this view.
        """
        try:
            return super().paginate_queryset(queryset, request, view)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=request.query_params.get(self.page_query_param, 1),
                message=str(exc)
            )
            raise NotFound(msg)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object with enhanced format.
        
        Response format:
        {
            "count": 150,           # Total number of items
            "page": 2,              # Current page number
            "pages": 15,            # Total number of pages
            "page_size": 10,        # Items per page
            "has_next": true,       # Whether there is a next page
            "has_previous": true,   # Whether there is a previous page
            "next_page": 3,         # Next page number (null if no next)
            "previous_page": 1,     # Previous page number (null if no previous)
            "results": [...]        # Actual data
        }
        """
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'page_size': self.page.paginator.per_page,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        """
        Return the OpenAPI schema for paginated responses.
        
        This ensures proper API documentation generation.
        """
        return {
            'type': 'object',
            'required': ['count', 'page', 'pages', 'page_size', 'has_next', 'has_previous', 'results'],
            'properties': {
                'count': {
                    'type': 'integer',
                    'description': 'Total number of items across all pages',
                    'example': 150
                },
                'page': {
                    'type': 'integer',
                    'description': 'Current page number (1-based)',
                    'example': 2
                },
                'pages': {
                    'type': 'integer', 
                    'description': 'Total number of pages',
                    'example': 15
                },
                'page_size': {
                    'type': 'integer',
                    'description': 'Number of items per page',
                    'example': 10
                },
                'has_next': {
                    'type': 'boolean',
                    'description': 'Whether there is a next page',
                    'example': True
                },
                'has_previous': {
                    'type': 'boolean',
                    'description': 'Whether there is a previous page',
                    'example': True
                },
                'next_page': {
                    'type': 'integer',
                    'nullable': True,
                    'description': 'Next page number (null if no next page)',
                    'example': 3
                },
                'previous_page': {
                    'type': 'integer',
                    'nullable': True,
                    'description': 'Previous page number (null if no previous page)',
                    'example': 1
                },
                'results': {
                    **schema,
                    'description': 'Array of items for current page'
                },
            },
        }

    def get_html_context(self):
        """
        Return context for HTML template rendering (browsable API).
        """
        base_context = super().get_html_context()
        base_context.update({
            'page_size': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
        })
        return base_context


class LargePagination(DefaultPagination):
    """
    Pagination class for large datasets.
    
    Uses larger page sizes for better performance with big collections.
    """
    page_size = 500
    max_page_size = 2000


class SmallPagination(DefaultPagination):
    """
    Pagination class for small datasets or detailed views.
    
    Uses smaller page sizes for better user experience.
    """
    page_size = 20
    max_page_size = 100


class NoPagination(PageNumberPagination):
    """
    Pagination class that effectively disables pagination.
    
    Returns all results in a single page. Use with caution on large datasets.
    """
    page_size = None
    page_size_query_param = None
    max_page_size = None

    def paginate_queryset(self, queryset, request, view=None):
        """
        Don't paginate the queryset, return None to indicate no pagination.
        """
        return None

    def get_paginated_response(self, data):
        """
        Return a non-paginated response.
        """
        return Response(data)


class CursorPaginationEnhanced(PageNumberPagination):
    """
    Enhanced cursor-based pagination for large datasets.
    
    Better performance for large datasets but doesn't support jumping to arbitrary pages.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
    cursor_query_param = 'cursor'
    ordering = '-created_at'  # Default ordering, should be overridden

    def get_paginated_response(self, data):
        """
        Return cursor-paginated response with enhanced format.
        """
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        """
        Return the OpenAPI schema for cursor-paginated responses.
        """
        return {
            'type': 'object',
            'required': ['results'],
            'properties': {
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': 'URL to next page of results',
                    'example': 'http://api.example.org/accounts/?cursor=cD0yMDIzLTEyLTE1KzAyJTNBMDA%3D'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': 'URL to previous page of results',
                    'example': 'http://api.example.org/accounts/?cursor=bD0yMDIzLTEyLTEzKzAyJTNBMDA%3D'
                },
                'page_size': {
                    'type': 'integer',
                    'description': 'Number of items per page',
                    'example': 100
                },
                'results': {
                    **schema,
                    'description': 'Array of items for current page'
                },
            },
        }


# Export all pagination classes
__all__ = [
    'DefaultPagination',
    'LargePagination', 
    'SmallPagination',
    'NoPagination',
    'CursorPaginationEnhanced',
]
