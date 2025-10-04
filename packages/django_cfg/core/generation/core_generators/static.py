"""
Static files settings generator.

Handles STATIC_*, MEDIA_*, and WhiteNoise configuration.
Size: ~70 lines (focused on static files)
"""

from typing import Dict, Any, TYPE_CHECKING

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
        settings = {
            "STATIC_URL": "/static/",
            "MEDIA_URL": "/media/",
            # WhiteNoise configuration
            "STATICFILES_STORAGE": "whitenoise.storage.CompressedManifestStaticFilesStorage",
            "WHITENOISE_USE_FINDERS": True,
            "WHITENOISE_AUTOREFRESH": self.config.debug,
            "WHITENOISE_MAX_AGE": 0 if self.config.debug else 3600,  # No cache in debug, 1 hour in prod
        }

        # Set paths relative to base directory
        if self.config._base_dir:
            settings.update({
                "STATIC_ROOT": self.config._base_dir / "staticfiles",
                "MEDIA_ROOT": self.config._base_dir / "media",
                "STATICFILES_DIRS": [
                    self.config._base_dir / "static",
                ],
            })

        # Static files finders
        settings["STATICFILES_FINDERS"] = [
            "django.contrib.staticfiles.finders.FileSystemFinder",
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ]

        return settings


__all__ = ["StaticFilesGenerator"]
