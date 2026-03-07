"""
RouteDebugMiddleware — logs 404 responses with URL patterns context.

Active only when DEBUG=True. Helps trace "Not Found" errors caused by
misconfigured URL routers (e.g. nested DRF routers leaking between groups).

Usage (auto-enabled by django-cfg when debug=True and debug_log_404=True):
    # config.py
    class MyConfig(DjangoConfig):
        debug_log_404: bool = True  # default True in DEBUG mode
"""

import logging

from django.conf import settings
from django.http import Http404

logger = logging.getLogger("django_cfg.debug_404")


class RouteDebugMiddleware:
    """
    Intercepts 404 responses in DEBUG mode and logs:
    - The full request path
    - HTTP method
    - Referer (if any)
    - Candidate URL patterns that almost matched (prefix match)

    This makes it easy to spot router misconfiguration where routes
    end up under the wrong API group prefix (e.g. /api/scenes/projects/.../characters/
    instead of /api/projects/projects/.../characters/).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404 and settings.DEBUG:
            self._log_404(request)

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404) and settings.DEBUG:
            self._log_404(request, exception)
        return None

    def _log_404(self, request, exception=None):
        path = request.path
        method = request.method
        referer = request.META.get("HTTP_REFERER", "")

        candidates = self._find_candidate_patterns(path)

        lines = [
            f"404 {method} {path}",
        ]
        if referer:
            lines.append(f"  Referer: {referer}")
        if exception:
            lines.append(f"  Exception: {exception}")

        if candidates:
            lines.append(f"  Partial matches ({len(candidates)} patterns share prefix):")
            for pattern, view_name in candidates[:10]:
                lines.append(f"    {pattern}  →  {view_name}")
        else:
            lines.append("  No partial matches found in URL conf.")

        logger.warning("\n".join(lines))

    @staticmethod
    def _find_candidate_patterns(path: str) -> list:
        """Find URL patterns whose string prefix overlaps with the 404 path."""
        from django.urls import get_resolver

        resolver = get_resolver()
        candidates = []

        # Split path into segments, look for patterns that share leading segments
        path_parts = [p for p in path.split("/") if p]
        if not path_parts:
            return []

        try:
            flat = _flatten_patterns(resolver)
        except Exception:
            return []

        for pattern_str, view_name in flat:
            pattern_parts = [p for p in pattern_str.split("/") if p and "<" not in p]
            # Match if first 2 segments overlap
            overlap = min(len(path_parts), len(pattern_parts), 2)
            if overlap and path_parts[:overlap] == pattern_parts[:overlap]:
                candidates.append((pattern_str, view_name))

        return candidates


def _flatten_patterns(resolver, prefix="") -> list:
    """Recursively flatten URL resolver into (pattern_string, name) pairs."""
    result = []
    for pattern in resolver.url_patterns:
        full = prefix + str(pattern.pattern)
        if hasattr(pattern, "url_patterns"):
            result.extend(_flatten_patterns(pattern, full))
        else:
            name = getattr(pattern, "name", "") or ""
            result.append((full, name))
    return result
