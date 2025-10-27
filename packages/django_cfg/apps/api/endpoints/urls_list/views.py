"""
Django CFG URLs List DRF View

DRF browsable API view for listing all Django URLs with Tailwind theme support.
"""

from typing import Any, Dict, List
from urllib.parse import urljoin

from django.conf import settings
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cfg.core.integration import get_current_version

from .serializers import URLsListSerializer


class DRFURLsListView(APIView):
    """
    Django CFG URLs list endpoint with DRF Browsable API.

    Lists all registered Django URLs with their:
    - Pattern
    - Name
    - View/ViewSet
    - Full URL
    - HTTP methods

    This endpoint uses DRF Browsable API with Tailwind CSS theme! 🎨
    """

    permission_classes = [AllowAny]  # Public endpoint (can be restricted)
    serializer_class = URLsListSerializer  # For schema generation

    def get(self, request):
        """Return all registered URLs."""
        try:
            config = getattr(settings, 'config', None)

            # Get base URL from config or settings
            base_url = getattr(config, 'site_url', None) if config else None
            if not base_url:
                base_url = request.build_absolute_uri('/').rstrip('/')

            urls_data = {
                "status": "success",
                "service": config.project_name if config else "Django CFG",
                "version": get_current_version(),
                "base_url": base_url,
                "total_urls": 0,
                "urls": []
            }

            # Extract all URLs
            url_patterns = self._get_all_urls()
            urls_data["urls"] = url_patterns
            urls_data["total_urls"] = len(url_patterns)

            return Response(urls_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_all_urls(self, urlpatterns=None, prefix='', namespace=None) -> List[Dict[str, Any]]:
        """
        Recursively extract all URL patterns from Django URLconf.

        Args:
            urlpatterns: URL patterns to process
            prefix: URL prefix from parent resolvers
            namespace: Current namespace

        Returns:
            List of URL pattern dictionaries
        """
        if urlpatterns is None:
            urlpatterns = get_resolver().url_patterns

        url_list = []

        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                # Recursively process URL resolver (include())
                new_prefix = prefix + str(pattern.pattern)
                new_namespace = f"{namespace}:{pattern.namespace}" if namespace and pattern.namespace else pattern.namespace or namespace

                url_list.extend(
                    self._get_all_urls(
                        pattern.url_patterns,
                        prefix=new_prefix,
                        namespace=new_namespace
                    )
                )
            elif isinstance(pattern, URLPattern):
                # Extract URL pattern details
                url_pattern = prefix + str(pattern.pattern)
                url_name = pattern.name

                # Build full name with namespace
                if namespace and url_name:
                    full_name = f"{namespace}:{url_name}"
                else:
                    full_name = url_name

                # Get view information
                view_info = self._get_view_info(pattern)

                url_list.append({
                    "pattern": url_pattern,
                    "name": url_name,
                    "full_name": full_name,
                    "namespace": namespace,
                    "view": view_info["view"],
                    "view_class": view_info["view_class"],
                    "methods": view_info["methods"],
                    "module": view_info["module"],
                })

        return url_list

    def _get_view_info(self, pattern: URLPattern) -> Dict[str, Any]:
        """
        Extract view information from URL pattern.

        Args:
            pattern: URLPattern instance

        Returns:
            Dictionary with view information
        """
        view_info = {
            "view": None,
            "view_class": None,
            "methods": [],
            "module": None,
        }

        try:
            callback = pattern.callback

            if callback is None:
                return view_info

            # Get view name
            if hasattr(callback, '__name__'):
                view_info["view"] = callback.__name__
            elif hasattr(callback, '__class__'):
                view_info["view"] = callback.__class__.__name__

            # Get view class (for CBV/ViewSets)
            if hasattr(callback, 'cls'):
                view_info["view_class"] = callback.cls.__name__

                # Get HTTP methods from ViewSet/APIView
                if hasattr(callback.cls, 'http_method_names'):
                    view_info["methods"] = callback.cls.http_method_names

                # Get module
                if hasattr(callback.cls, '__module__'):
                    view_info["module"] = callback.cls.__module__

            # For function-based views
            elif hasattr(callback, '__module__'):
                view_info["module"] = callback.__module__

                # Try to determine methods from decorator
                if hasattr(callback, 'methods'):
                    view_info["methods"] = list(callback.methods)
                else:
                    view_info["methods"] = ['GET']  # Default for FBV

        except Exception:
            pass

        return view_info


class DRFURLsListCompactView(APIView):
    """
    Compact URLs list endpoint - just patterns and names.

    This endpoint uses DRF Browsable API with Tailwind CSS theme! 🎨
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Return compact URL list."""
        try:
            url_patterns = self._get_compact_urls()

            return Response({
                "status": "success",
                "total": len(url_patterns),
                "urls": url_patterns
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_compact_urls(self, urlpatterns=None, prefix='') -> List[Dict[str, str]]:
        """Extract URLs in compact format."""
        if urlpatterns is None:
            urlpatterns = get_resolver().url_patterns

        url_list = []

        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                new_prefix = prefix + str(pattern.pattern)
                url_list.extend(
                    self._get_compact_urls(pattern.url_patterns, prefix=new_prefix)
                )
            elif isinstance(pattern, URLPattern):
                url_pattern = prefix + str(pattern.pattern)
                url_list.append({
                    "pattern": url_pattern,
                    "name": pattern.name or "unnamed",
                })

        return url_list
