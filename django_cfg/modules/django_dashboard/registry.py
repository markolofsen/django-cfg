from importlib import import_module
from typing import Any, Callable, Dict

from .models.tab import DashboardTab


def _resolve(dotted_path: str) -> Callable:
    module_path, fn_name = dotted_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, fn_name)


class TabRegistry:
    def get_context(self, tab: DashboardTab, request: Any) -> Dict[str, Any]:
        if not tab.callback:
            return {}
        fn = _resolve(tab.callback)
        return fn(request)

    def has_permission(self, tab: DashboardTab, request: Any) -> bool:
        if tab.superuser_only:
            return bool(getattr(request.user, "is_superuser", False))
        if not tab.permission:
            return bool(getattr(request.user, "is_staff", False))
        fn = _resolve(tab.permission)
        return bool(fn(request))
