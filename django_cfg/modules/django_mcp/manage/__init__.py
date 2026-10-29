"""Self-service management of MCP access: keys, OAuth connections, usage.

A project mounts :func:`manage_urlpatterns` (or lets the profile do it with
``enable_manage``) and its signed-in users get the whole panel without views.
See ``@docs/manage.md``.
"""

from .store import AccessStore, StoreRefusal, load_store, supports
from .urls import manage_urlpatterns

__all__ = ["AccessStore", "StoreRefusal", "load_store", "supports", "manage_urlpatterns"]
