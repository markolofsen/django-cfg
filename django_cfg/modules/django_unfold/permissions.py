"""Auto-generated permission callbacks for Unfold navigation items.

These are resolved dynamically by import_string from unfold.sites.
"""

from django.http import HttpRequest


class _PermissionCache:
    """Dynamically generate permission checkers for admin models."""

    @staticmethod
    def _has_model_perm(request: HttpRequest, app_label: str, model: str, action: str = "view") -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_perm(f"{app_label}.{action}_{model}")

    @classmethod
    def make_checker(cls, app_label: str, model: str):
        def checker(request: HttpRequest) -> bool:
            return cls._has_model_perm(request, app_label, model)
        checker.__name__ = f"can_view_{app_label}_{model}"
        checker.__qualname__ = f"_PermissionCache.{checker.__name__}"
        return checker


def __getattr__(name: str):
    """Dynamically resolve can_view_<app>_<model> permission callbacks."""
    import re
    match = re.match(r"^can_view_(?P<app>[a-z_]+)_(?P<model>[a-z]+)$", name)
    if match:
        return _PermissionCache.make_checker(match.group("app"), match.group("model"))
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
