"""django_grpc.config.routing — Cross-process routing configuration.

C-06 fix: the CrossProcessConfig that lives here was a duplicate of the one in
services/routing/config.py. The two models had different fields and the router
actually imported the services/routing/config.py version — this one was never
used. Removed to avoid confusion.

The canonical CrossProcessConfig is in:
    django_cfg.modules.django_grpc.services.routing.config.CrossProcessConfig

It has the concrete fields the router needs (grpc_host, grpc_port,
rpc_method_name, timeout, enable_logging).
"""

from __future__ import annotations

# Re-export the canonical definition so any code that imported from here
# still works without changes.
from django_cfg.modules.django_grpc.services.routing.config import CrossProcessConfig

__all__ = ["CrossProcessConfig"]
