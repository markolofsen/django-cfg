"""
Version checker for django-cfg library.

Checks PyPI for the latest version and caches results for 24 hours using cachetools.
"""

import importlib.metadata
from typing import Any, Dict, Optional

import requests
from cachetools import TTLCache


class VersionChecker:
    """
    Checks for library updates on PyPI with 1-hour caching using cachetools.
    """

    # Cache for 1 hour (3600 seconds)
    CACHE_TTL = 3600

    def __init__(self):
        """Initialize version checker with TTL cache."""
        self._cache = TTLCache(maxsize=10, ttl=self.CACHE_TTL)

    def get_package_name(self) -> str:
        """
        Get package name automatically using importlib.metadata.
        
        Returns:
            Package name for PyPI
        """
        try:
            # Get package metadata
            metadata = importlib.metadata.metadata('django-cfg')
            return metadata['Name']
        except importlib.metadata.PackageNotFoundError:
            # Fallback to hardcoded name
            return 'django-cfg'

    def get_latest_version(self) -> Optional[str]:
        """
        Get latest version from PyPI with caching.
        
        Returns:
            Latest version string or None if unavailable
        """
        # Check cache first
        cached_version = self._cache.get('latest_version')
        if cached_version:
            return cached_version

        try:
            package_name = self.get_package_name()
            url = f"https://pypi.org/pypi/{package_name}/json"

            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            version = data["info"]["version"]

            # Cache the result
            self._cache['latest_version'] = version

            return version

        except Exception:
            # Silently fail - version checking is not critical
            return None

    def get_current_version(self) -> Optional[str]:
        """
        Get current installed version using importlib.metadata.
        
        Returns:
            Current version string or None if unavailable
        """
        try:
            # First try to get from __version__
            from django_cfg import __version__
            return __version__
        except ImportError:
            try:
                # Fallback to importlib.metadata
                return importlib.metadata.version('django-cfg')
            except importlib.metadata.PackageNotFoundError:
                return None

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check if an update is available.
        
        Returns:
            Dictionary with update information
        """
        current = self.get_current_version()
        latest = self.get_latest_version()

        result = {
            'current_version': current,
            'latest_version': latest,
            'update_available': False,
            'update_url': None,
        }

        if current and latest and current != latest:
            # Simple version comparison (assumes semantic versioning)
            try:
                current_parts = [int(x) for x in current.split('.')]
                latest_parts = [int(x) for x in latest.split('.')]

                # Pad shorter version with zeros
                max_len = max(len(current_parts), len(latest_parts))
                current_parts.extend([0] * (max_len - len(current_parts)))
                latest_parts.extend([0] * (max_len - len(latest_parts)))

                if latest_parts > current_parts:
                    result['update_available'] = True
                    package_name = self.get_package_name()
                    result['update_url'] = f"https://pypi.org/project/{package_name}/"

            except (ValueError, AttributeError):
                # Version comparison failed - skip update check
                pass

        return result


# Global instance
_version_checker = VersionChecker()


def get_version_info() -> Dict[str, Any]:
    """
    Get version information and update status.
    
    Returns:
        Dictionary with version and update information
    """
    return _version_checker.check_for_updates()


def get_latest_version() -> Optional[str]:
    """
    Get latest version from PyPI.
    
    Returns:
        Latest version string or None if unavailable
    """
    return _version_checker.get_latest_version()


def get_current_version() -> Optional[str]:
    """
    Get current installed version.
    
    Returns:
        Current version string or None if unavailable
    """
    return _version_checker.get_current_version()
