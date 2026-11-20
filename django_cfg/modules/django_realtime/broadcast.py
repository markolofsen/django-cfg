"""Hints from model changes: `broadcasts(Model, topic)`, `touch(topic)` and `suppress()`.

    # apps/orders/realtime.py
    order = topic("orders:{order_id:int}", allow=...)
    broadcasts(Order, order, params=lambda o: {"order_id": o.pk})

Every `post_save` / `post_delete` of the model schedules a hint on the topic after the commit. Within one
transaction a topic gets one message however many rows changed: later changes fold into the pending one (the last
event wins). Outside a transaction the hint is appended at once.

Writes that send no signal (`QuerySet.update()`, `bulk_create`, `bulk_update`, database-level cascades, raw SQL)
announce themselves with `touch(topic)`, which folds the same way. `with suppress():` mutes the model receivers
for a block (an import), typically followed by one `touch()`; it does not mute `touch()` or `publish()`.
"""

from __future__ import annotations

import contextlib
import contextvars
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, Tuple, Type, Union

from pydantic import BaseModel, ValidationError

from .publishing import Target, append, resolve_target, sender_cid, validate_event
from .registry import BoundTopic, Topic, TopicDeclarationError

_suppressed: contextvars.ContextVar[int] = contextvars.ContextVar("realtime_suppressed", default=0)

EventFactory = Callable[[Any, str], Union[BaseModel, Mapping[str, Any], None]]


class _Pending:
    """The on_commit callback of one topic in one transaction; later changes update it instead of adding more."""

    __slots__ = ("bound", "payload", "origin_cid")

    def __init__(self, bound: BoundTopic, payload: BaseModel, origin_cid: Optional[str]) -> None:
        self.bound = bound
        self.payload = payload
        self.origin_cid = origin_cid

    def __call__(self) -> None:
        append(self.bound, self.payload, origin_cid=self.origin_cid)


def _schedule(bound: BoundTopic, payload: BaseModel, using: Optional[str]) -> Optional[str]:
    from django.db import transaction

    origin = sender_cid()
    conn = transaction.get_connection(using)
    if not conn.in_atomic_block:
        return append(bound, payload, origin_cid=origin)
    # run_on_commit holds (savepoint ids, callback, robust); a rolled-back savepoint already dropped its own.
    for entry in conn.run_on_commit:
        pending = entry[1]
        if isinstance(pending, _Pending) and pending.bound.name == bound.name:
            pending.payload = payload
            if pending.origin_cid != origin:  # two senders folded: neither may be skipped
                pending.origin_cid = None
            return None
    transaction.on_commit(_Pending(bound, payload, origin), using=using, robust=True)
    return None


def touch(
    target: Target,
    event: Union[BaseModel, Mapping[str, Any], None] = None,
    *,
    using: Optional[str] = None,
) -> Optional[str]:
    """A hint for changes no signal reports. Folds with the transaction's other hints on the same topic.

    Returns the offset when appended at once (no transaction), else None.
    """
    bound = resolve_target(target)
    return _schedule(bound, validate_event(bound.topic, event), using)


@contextlib.contextmanager
def suppress() -> Iterator[None]:
    """Mute every `broadcasts()` receiver in this context (thread or task); nests."""
    token = _suppressed.set(_suppressed.get() + 1)
    try:
        yield
    finally:
        _suppressed.reset(token)


def is_suppressed() -> bool:
    return _suppressed.get() > 0


def _default_params(model: Type[Any], topic: Topic) -> Callable[[Any], Dict[str, Any]]:
    """Each parameter from the model attribute of that name; a single parameter falls back to the pk."""
    names = [name for name, _ in topic.params]
    fields = {"pk"}
    for f in model._meta.concrete_fields:
        fields.update({f.name, f.attname})
    missing = [n for n in names if n not in fields]
    if missing and len(names) == 1:
        return lambda instance: {names[0]: instance.pk}
    if missing:
        raise TopicDeclarationError(
            f"broadcasts({model.__name__}, {topic.pattern!r}): no field for {', '.join(missing)}; pass params="
        )
    return lambda instance: {n: getattr(instance, n) for n in names}


class Broadcast:
    """A connected `broadcasts()` declaration; `disconnect()` removes its receivers."""

    def __init__(self, model, resolve: Callable[[Any], Target], event: Optional[EventFactory], on: Tuple[str, ...]):
        self.model = model
        self.on = on
        self._resolve = resolve
        self._event = event
        self._uid = f"django_realtime.broadcasts:{id(self)}"

    def _fire(self, instance: Any, action: str, using: Optional[str]) -> None:
        if is_suppressed():
            return
        bound = resolve_target(self._resolve(instance))
        raw = self._event(instance, action) if self._event is not None else None
        _schedule(bound, validate_event(bound.topic, raw), using)

    def _on_save(self, sender, instance, raw=False, using=None, **kwargs) -> None:
        if not raw:  # loaddata
            self._fire(instance, "save", using)

    def _on_delete(self, sender, instance, using=None, **kwargs) -> None:
        self._fire(instance, "delete", using)

    def connect(self) -> "Broadcast":
        from django.db.models.signals import post_delete, post_save

        if "save" in self.on:
            post_save.connect(self._on_save, sender=self.model, weak=False, dispatch_uid=self._uid)
        if "delete" in self.on:
            post_delete.connect(self._on_delete, sender=self.model, weak=False, dispatch_uid=self._uid)
        return self

    def disconnect(self) -> None:
        from django.db.models.signals import post_delete, post_save

        post_save.disconnect(sender=self.model, dispatch_uid=self._uid)
        post_delete.disconnect(sender=self.model, dispatch_uid=self._uid)


def broadcasts(
    model: Union[Type[Any], str],
    topic: Union[Topic, Callable[[Any], Target]],
    *,
    params: Optional[Callable[[Any], Dict[str, Any]]] = None,
    event: Optional[EventFactory] = None,
    on: Tuple[str, ...] = ("save", "delete"),
) -> Broadcast:
    """Send a hint on `topic` after each committed save or delete of `model` (one per topic per transaction).

    `topic` is a Topic (parameters from `params(instance)`, else from the model fields of the same names, else the
    pk for a single parameter) or a function `instance -> topic name or BoundTopic`. `event(instance, action)`
    builds the payload when the topic's event is not the empty hint; `action` is "save" or "delete".
    """
    if isinstance(model, str):
        from django.apps import apps

        model = apps.get_model(model)
    unknown = set(on) - {"save", "delete"}
    if unknown or not on:
        raise TopicDeclarationError(f"broadcasts(): on= takes 'save' and/or 'delete', got {on!r}")
    if isinstance(topic, Topic):
        if event is None:
            try:
                topic.event.model_validate({})
            except ValidationError as exc:
                raise TopicDeclarationError(
                    f"broadcasts({model.__name__}, {topic.pattern!r}): {topic.event.__name__} needs fields; pass event="
                ) from exc
        if topic.params:
            build = params or _default_params(model, topic)
            resolve: Callable[[Any], Target] = lambda instance: topic(**build(instance))  # noqa: E731
        else:
            resolve = lambda instance: topic  # noqa: E731
    elif callable(topic):
        if params is not None:
            raise TopicDeclarationError("broadcasts(): params= applies to a Topic, not to a topic function")
        resolve = topic
    else:
        raise TopicDeclarationError(f"broadcasts(): topic must be a Topic or a function, got {topic!r}")
    return Broadcast(model, resolve, event, tuple(on)).connect()


__all__ = ["Broadcast", "broadcasts", "is_suppressed", "suppress", "touch"]
