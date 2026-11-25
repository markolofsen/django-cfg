"""``notion.connect(Model, adapter=..., route=...)``: no hand-written signals."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from django.db.models.signals import post_save

from . import conf
from .lead import NotionLead
from .outbox import capture

logger = logging.getLogger("django_cfg.modules.django_notion")

Adapter = Callable[[Any], NotionLead]
Route = Callable[[Any], Optional[str]]

_connections: Dict[str, dict] = {}


def connect(model, *, adapter: Adapter, route: Optional[Route] = None, project: Optional[str] = None, notify: bool = True) -> None:
    """Mirror new ``model`` rows into Notion.

    ``adapter(instance) -> NotionLead``; ``route(instance) -> target name | None`` (None = do not send). Without
    ``route`` the single configured target is used. Fires once, when the row is created. ``notify=False`` sends the
    row to Notion only: no Telegram, admin email or acknowledgement, for a model whose own code already announces it.
    """
    label = model._meta.label_lower

    def handler(sender, instance, created, raw=False, **kwargs):
        if not created or raw:
            return
        try:
            cfg = conf.get_notion_config()
            if route is not None:
                target = route(instance)
            elif len(cfg.targets) == 1:
                target = next(iter(cfg.targets))
            else:
                raise ValueError("several Notion targets are configured: pass route=")
            if target is None:
                return
            lead = adapter(instance)
            if not isinstance(lead, NotionLead):
                lead = NotionLead(**lead)
        except Exception:
            logger.exception("django_notion: adapter/route failed for %s pk=%s (the lead itself is saved)", label, getattr(instance, "pk", "?"))
            return
        capture(instance, lead, target, project=project, notify=notify)

    _connections[label] = {"adapter": adapter, "route": route, "notify": notify}
    post_save.connect(handler, sender=model, weak=False, dispatch_uid=f"django_notion:{label}")


def disconnect(model) -> None:
    label = model._meta.label_lower
    post_save.disconnect(sender=model, dispatch_uid=f"django_notion:{label}")
    _connections.pop(label, None)
