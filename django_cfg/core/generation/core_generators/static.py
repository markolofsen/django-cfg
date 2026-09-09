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

        static_backend = (
            "whitenoise.storage.CompressedStaticFilesStorage" if is_development
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )

        settings = {
            "STATIC_URL": "/staticfiles/",
            "MEDIA_URL": self.config.media_url,
            "WHITENOISE_USE_FINDERS": True,
            "WHITENOISE_AUTOREFRESH": is_development,
            "WHITENOISE_MAX_AGE": 0 if is_development else 3600,  # No cache in debug, 1 hour in prod
        }

        # STORAGES (Django 4.2+) supersedes STATICFILES_STORAGE; defining both
        # would make the legacy key a silent no-op.
        settings["STORAGES"] = self._build_storages(static_backend)

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

        # Object storage serves media from its own host; MEDIA_ROOT stays for
        # local mode only.
        backend = self._get_backend()
        if backend is not None:
            media_url = backend.media_url()
            if media_url:
                settings["MEDIA_URL"] = media_url

        return settings

    def _get_backend(self):
        """The configured object-storage backend, or None for local storage."""
        storage = getattr(self.config, "storage", None)
        return getattr(storage, "backend", None) if storage else None

    def _build_storages(self, static_backend: str) -> Dict[str, Any]:
        """
        Build the STORAGES dict.

        With no backend configured this is the local-filesystem default plus
        WhiteNoise — identical in effect to the pre-STORAGES settings.
        """
        storages: Dict[str, Any] = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": static_backend},
        }

        backend = self._get_backend()
        if backend is None:
            return storages

        backend.check_dependencies()

        from django_cfg.models.django.storage_backend import S3_BACKEND

        options = backend.storage_options()
        client_config = backend.client_config()
        if client_config is not None:
            options = {**options, "client_config": client_config}

        storages["default"] = {"BACKEND": S3_BACKEND, "OPTIONS": options}

        if backend.serve_static:
            static_options = {
                **options,
                # Keep the environment segment: a bare "static" would put every
                # environment's collectstatic output in one place.
                "location": backend.static_key_prefix,
                "querystring_auth": False,
                # collectstatic re-uploads the same names every deploy. With
                # file_overwrite=False django-storages appends a random suffix
                # instead of replacing, so the bucket accumulates copies and the
                # manifest points at stale ones (django-storages#291).
                "file_overwrite": True,
            }
            storages["staticfiles"] = {"BACKEND": S3_BACKEND, "OPTIONS": static_options}

        return storages


__all__ = ["StaticFilesGenerator"]
