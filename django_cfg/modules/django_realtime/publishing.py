"""`publish()`: validate an event against its topic and append it to the topic's log after the transaction commits."""

from __future__ import annotations

import contextvars
import hashlib
from typing import Any, Callable, List, Mapping, Optional, Union

from pydantic import BaseModel, ValidationError

from .backends import get_backend, get_realtime_config
from .registry import BoundTopic, InvalidEvent, Topic, UnknownTopic, registry

#: Called with (topic name, validated event, offset) after each append; `testing.realtime_outbox` listens here.
_listeners: List[Callable[[str, BaseModel, str], None]] = []

Target = Union[str, Topic, BoundTopic]

#: The sender of the request being served: a `middleware.CidClaim` (verified when read), or a plain id set by
#: trusted code (tests, a job acting for a known socket).
current_cid: contextvars.ContextVar[Any] = contextvars.ContextVar("realtime_cid", default=None)


def sender_cid() -> Optional[str]:
    """The verified connection id of the current sender, or None."""
    value = current_cid.get()
    if value is None or isinstance(value, str):
        return value
    return value.resolve()


def resolve_target(target: Target) -> BoundTopic:
    """A topic name, a parameterless Topic or a BoundTopic -> BoundTopic; UnknownTopic otherwise."""
    if isinstance(target, BoundTopic):
        return target
    if isinstance(target, Topic):
        if target.params:
            names = ", ".join(name for name, _ in target.params)
            raise UnknownTopic(f"topic {target.pattern!r} needs parameters ({names}): call it first")
        return target()
    if isinstance(target, str):
        return registry.resolve(target)
    raise UnknownTopic(f"not a topic: {target!r}")


def validate_event(topic: Topic, event: Union[BaseModel, Mapping[str, Any], None]) -> BaseModel:
    """The event as an instance of the topic's model; InvalidEvent when it is anything else."""
    model = topic.event
    if event is None:
        event = {}
    if isinstance(event, model):
        return event
    if isinstance(event, BaseModel):
        raise InvalidEvent(f"topic {topic.pattern!r} takes {model.__name__}, got {type(event).__name__}")
    if not isinstance(event, Mapping):
        raise InvalidEvent(f"topic {topic.pattern!r} takes {model.__name__} or a dict, got {type(event).__name__}")
    try:
        return model.model_validate(dict(event))
    except ValidationError as exc:
        raise InvalidEvent(f"topic {topic.pattern!r}: {exc}") from exc


def publish(
    target: Target,
    event: Union[BaseModel, Mapping[str, Any], None] = None,
    *,
    on_commit: bool = True,
    using: Optional[str] = None,
    exclude_sender: bool = True,
) -> Optional[str]:
    """Publish `event` to a topic. Sync; usable from views, signals, admin actions and RQ jobs.

    Raises UnknownTopic or InvalidEvent at call time. Inside an atomic block (and `on_commit=True`) the append runs
    after the commit and the offset is not known yet (returns None); a failed append is then logged by Django's
    robust on_commit. Outside a transaction, or with `on_commit=False`, it appends now, raises on a backend
    failure and returns the offset. A request that sent `X-Realtime-Cid` is the sender: its own socket is skipped
    (`exclude_sender=False` delivers to it too).
    """
    bound = resolve_target(target)
    payload = validate_event(bound.topic, event)
    data = payload.model_dump(mode="json")
    history = bound.topic.history or get_realtime_config().default_history
    origin_cid = sender_cid() if exclude_sender else None

    def send() -> str:
        return append(bound, payload, data=data, history=history, origin_cid=origin_cid)

    if on_commit:
        from django.db import transaction

        if transaction.get_connection(using).in_atomic_block:
            transaction.on_commit(send, using=using, robust=True)
            return None
    return send()


def append(bound: BoundTopic, payload: BaseModel, *, data: Optional[dict] = None, history: Optional[int] = None,
           origin_cid: Optional[str] = None) -> str:
    """Append a validated event now and tell the listeners; the one write path under `publish()` and `touch()`."""
    if data is None:
        data = payload.model_dump(mode="json")
    if history is None:
        history = bound.topic.history or get_realtime_config().default_history
    offset = get_backend().append(bound.name, data, history=history, origin_cid=origin_cid)
    for listener in list(_listeners):
        listener(bound.name, payload, offset)
    return offset


def session_hash(session_key: str) -> str:
    """How a socket remembers its session without holding the key."""
    return hashlib.sha256(session_key.encode()).hexdigest()[:24]


def kick(*, user: Any = None, session_key: Optional[str] = None, everyone: bool = False) -> None:
    """Close sockets in every process with 4419: a user's (by pk), a session's, or every signed-in one.

    Called by the accounts receivers (`signals.py`) on logout, logout-all, password change and deactivation.
    """
    if everyone:
        payload: dict = {"all": True}
    elif user is not None:
        payload = {"user": str(getattr(user, "pk", user))}
    elif session_key:
        payload = {"session": session_hash(session_key)}
    else:
        raise ValueError("kick() needs user, session_key or everyone=True")
    get_backend().kick(payload)


__all__ = ["append", "current_cid", "sender_cid", "kick", "publish", "resolve_target", "session_hash", "validate_event"]
