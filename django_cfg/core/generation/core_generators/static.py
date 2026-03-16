"""
Static files settings generator.

Handles STATIC_*, MEDIA_*, and WhiteNoise configuration.
Size: ~70 lines (focused on static files)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class StaticFilesGenerator:
    """
    Generates static files settings.

    Responsibilities:
    - STATIC_URL, STATIC_ROOT, STATICFILES_DIRS
    - MEDIA_URL, MEDIA_ROOT
    - WhiteNoise configuration
    - Static files finders

    Example:
        ```python
        generator = StaticFilesGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate static files settings.

        Returns:
            Dictionary with static files configuration

        Example:
            >>> generator = StaticFilesGenerator(config)
            >>> settings = generator.generate()
            >>> "STATIC_URL" in settings
            True
        """
        
        is_development = self.config.debug or self.config.is_development
        
        settings = {
            "STATIC_URL": "/staticfiles/",
            "MEDIA_URL": self.config.media_url,
            # WhiteNoise configuration - use simple storage in debug mode to avoid manifest caching
            "STATICFILES_STORAGE": (
                "whitenoise.storage.CompressedStaticFilesStorage" if is_development
                else "whitenoise.storage.CompressedManifestStaticFilesStorage"
            ),
            "WHITENOISE_USE_FINDERS": True,
            "WHITENOISE_AUTOREFRESH": is_development,
            "WHITENOISE_MAX_AGE": 0 if is_development else 3600,  # No cache in debug, 1 hour in prod
        }

        # Set paths relative to base directory (always set, auto-detects from manage.py)
        base_dir = self.config.base_dir

        # Note: Next.js admin static files are copied to static/nextjs_admin/
        # during generate_client command (if auto_build=True)
        # No need to add separate path to STATICFILES_DIRS

        # Only include STATICFILES_DIRS entries that exist on disk.
        # Django staticfiles.W004 fires for non-existent directories.
        static_dir = base_dir / "static"
        static_root = base_dir / "staticfiles"
        media_root = base_dir / "media"

        # Ensure directories exist so WhiteNoise doesn't warn at startup
        static_root.mkdir(parents=True, exist_ok=True)
        media_root.mkdir(parents=True, exist_ok=True)

        settings.update({
            "STATIC_ROOT": static_root,
            "MEDIA_ROOT": media_root,
            "STATICFILES_DIRS": [static_dir] if static_dir.exists() else [],
        })

        # Static files finders
        settings["STATICFILES_FINDERS"] = [
            "django.contrib.staticfiles.finders.FileSystemFinder",
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ]

        return settings


__all__ = ["StaticFilesGenerator"]
