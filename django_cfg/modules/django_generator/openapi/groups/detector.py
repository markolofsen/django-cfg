"""
Application Group Detector.

Detects which Django apps belong to which groups, with wildcard support.
"""

import fnmatch
import logging
from typing import Dict, List, Set

from ..config import OpenAPIConfig

logger = logging.getLogger(__name__)


class GroupDetector:
    """
    Detects Django apps for each configured group.

    Supports wildcard patterns like "django_cfg.*" to match multiple apps.

    Example:
        >>> config = OpenAPIConfig(
        ...     groups={
        ...         "cfg": OpenAPIGroupConfig(
        ...             apps=["django_cfg.*"],
        ...             title="Framework",
        ...         ),
        ...         "custom": OpenAPIGroupConfig(
        ...             apps=["myapp", "anotherapp"],
        ...             title="Custom",
        ...         ),
        ...     },
        ... )
        >>> detector = GroupDetector(config)
        >>> groups = detector.detect_groups(installed_apps)
        >>> print(groups["cfg"])  # ['django_cfg.admin', 'django_cfg.logging', ...]
    """

    def __init__(self, config: OpenAPIConfig):
        """
        Initialize detector with configuration.

        Args:
            config: OpenAPI configuration with groups
        """
        self.config = config

    def detect_groups(self, installed_apps: List[str]) -> Dict[str, List[str]]:
        """
        Detect which apps belong to which groups.

        Args:
            installed_apps: List of installed Django apps

        Returns:
            Dictionary mapping group names to lists of app names

        Example:
            >>> installed_apps = [
            ...     "django_cfg.admin",
            ...     "django_cfg.logging",
            ...     "myapp",
            ...     "anotherapp",
            ... ]
            >>> result = detector.detect_groups(installed_apps)
            >>> result["cfg"]
            ['django_cfg.admin', 'django_cfg.logging']
            >>> result["custom"]
            ['myapp', 'anotherapp']
        """
        result = {}
        app_set = set(installed_apps)

        for group in self.config.groups:
            matched_apps = self._match_apps(group.apps, app_set)
            result[group.name] = sorted(matched_apps)

            logger.info(
                f"Group '{group.name}': {len(matched_apps)} apps "
                f"matched from {len(group.apps)} patterns"
            )
            logger.debug(f"Group '{group.name}' apps: {matched_apps}")

        return result

    def _match_apps(self, patterns: List[str], installed_apps: Set[str]) -> List[str]:
        """
        Match apps using patterns (supports wildcards).

        Args:
            patterns: List of app patterns (e.g., ["django_cfg.*", "myapp"])
            installed_apps: Set of installed app names

        Returns:
            List of matched app names

        Example:
            >>> patterns = ["django_cfg.*", "myapp"]
            >>> installed_apps = {
            ...     "django_cfg.admin",
            ...     "django_cfg.logging",
            ...     "myapp",
            ...     "otherapp",
            ... }
            >>> result = detector._match_apps(patterns, installed_apps)
            >>> sorted(result)
            ['django_cfg.admin', 'django_cfg.logging', 'myapp']
        """
        matched = []

        for pattern in patterns:
            if "*" in pattern or "?" in pattern or "[" in pattern:
                # Wildcard pattern - use fnmatch
                matches = fnmatch.filter(installed_apps, pattern)
                matched.extend(matches)
                logger.debug(f"Pattern '{pattern}' matched {len(matches)} apps")
            else:
                # Exact match
                if pattern in installed_apps:
                    matched.append(pattern)
                    logger.debug(f"Exact match: '{pattern}'")
                else:
                    logger.warning(f"App '{pattern}' not found in INSTALLED_APPS")

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for app in matched:
            if app not in seen:
                seen.add(app)
                result.append(app)

        return result

    def validate_groups(self, installed_apps: List[str]) -> Dict[str, bool]:
        """
        Validate that all groups have at least one matched app.

        Args:
            installed_apps: List of installed Django apps

        Returns:
            Dictionary mapping group names to validation status

        Example:
            >>> validation = detector.validate_groups(installed_apps)
            >>> if not all(validation.values()):
            ...     print("Some groups have no apps!")
        """
        groups = self.detect_groups(installed_apps)
        return {name: len(apps) > 0 for name, apps in groups.items()}

    def get_ungrouped_apps(self, installed_apps: List[str]) -> List[str]:
        """
        Get list of apps that don't belong to any group.

        Args:
            installed_apps: List of installed Django apps

        Returns:
            List of ungrouped app names

        Example:
            >>> ungrouped = detector.get_ungrouped_apps(installed_apps)
            >>> if ungrouped:
            ...     print(f"Ungrouped apps: {ungrouped}")
        """
        groups = self.detect_groups(installed_apps)
        grouped_apps = set()
        for apps in groups.values():
            grouped_apps.update(apps)

        return sorted(set(installed_apps) - grouped_apps)


__all__ = [
    "GroupDetector",
]
