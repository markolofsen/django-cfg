"""Realtime for django-cfg: one WebSocket per client, typed topics, `publish()` from any Django code.

    # apps/orders/realtime.py (autodiscovered)
    from django_cfg.modules.django_realtime import topic
    orders = topic("orders:{order_id:int}", event=OrderEvent, allow=lambda user, order_id: ...)

    # anywhere sync: a view, a signal, an RQ job
    from django_cfg.modules.django_realtime import publish
    publish(orders(order_id=42), OrderEvent(kind="paid"))   # appended after the transaction commits
    broadcasts(Order, orders)                               # a hint per committed save/delete; touch() for update()

    # a DRF view whose cached reads a topic invalidates (x-realtime-invalidates -> tagged SWR keys)
    @invalidated_by("orders:{order_id}")

    # api/asgi.py
    application = realtime_asgi(get_asgi_application())

Config: `DjangoConfig.realtime` (`models/django/realtime.py`). Protocol: `protocol.py`. Tests: `testing.py`
(`realtime_outbox`, `WebSocketDriver`). Names resolve lazily so importing the package costs nothing.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .asgi import realtime_asgi
    from .broadcast import broadcasts, suppress, touch
    from .openapi import invalidated_by
    from .publishing import publish
    from .registry import BoundTopic, Hint, InvalidEvent, RealtimeError, Topic, UnknownTopic, topic

_LAZY = {
    "topic": ".registry",
    "Topic": ".registry",
    "BoundTopic": ".registry",
    "Hint": ".registry",
    "RealtimeError": ".registry",
    "UnknownTopic": ".registry",
    "InvalidEvent": ".registry",
    "publish": ".publishing",
    "broadcasts": ".broadcast",
    "touch": ".broadcast",
    "suppress": ".broadcast",
    "invalidated_by": ".openapi",
    "realtime_asgi": ".asgi",
}


def __getattr__(name: str):
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(module, __name__), name)


__all__ = sorted(_LAZY)
