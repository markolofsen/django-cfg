"""
django_cfg.startup.drf_patch — JWT-aware DRF authentication patch.

Ensures that AuthenticationFailed raised by non-JWT backends does not block
JWT authentication when the request carries a JWT Bearer token.
"""


def patch_drf_authentication() -> None:
    """Apply JWT-aware DRF authentication patch. Called after all apps are loaded."""
    try:
        from django_cfg.middleware.authentication import _patch_drf_authenticate
        _patch_drf_authenticate()
    except Exception:
        pass
