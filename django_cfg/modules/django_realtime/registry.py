"""Topics: the declared patterns, their event models and permission hooks, and the lookup by concrete name.

Declare topics in an app's `realtime.py` (autodiscovered like `admin.py`):

    from django_cfg.modules.django_realtime import topic

    orders = topic("orders:{order_id:int}", event=OrderEvent,
                   allow=lambda user, order_id: Order.objects.filter(pk=order_id, owner=user).exists())

A pattern is a literal base (`[a-z0-9_.-]+`) and `:`-separated segments, each a literal or a `{name}` /
`{name:int}` parameter. `allow(user, **params)` is a plain sync function; it runs in a worker thread and may
use the ORM. Without `allow` an authenticated user may subscribe; `anonymous=True` also admits visitors.
"""

from __future__ import annotations

import inspect
import re
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type

from pydantic import BaseModel, ConfigDict

from .protocol import TOPIC_RE

ParamType = Literal["str", "int"]

_BASE_RE = re.compile(r"^[a-z0-9_.-]+$")
_LITERAL_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_PARAM_RE = re.compile(r"^\{([a-z_][a-z0-9_]*)(?::(str|int))?\}$")
_VALUE_RE = {"str": re.compile(r"^[A-Za-z0-9_.-]+$"), "int": re.compile(r"^-?[0-9]+$")}


class RealtimeError(Exception):
    """Base of every realtime error a caller may catch."""


class UnknownTopic(RealtimeError):
    """No declared topic matches this name."""


class InvalidEvent(RealtimeError):
    """The event does not validate against the topic's model."""


class TopicDeclarationError(RealtimeError, TypeError):
    """A `topic()` call that can never work (bad pattern, duplicate, `allow` signature)."""


class Hint(BaseModel):
    """The default event: no payload. The client refetches over REST."""

    model_config = ConfigDict(extra="forbid", title="RealtimeHint")


@dataclass(frozen=True)
class BoundTopic:
    """A topic with its parameters filled in: what `publish()` and `sub` address."""

    topic: "Topic"
    name: str
    params: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.name


class Topic:
    """One declared topic pattern."""

    def __init__(
        self,
        pattern: str,
        *,
        event: Type[BaseModel] = Hint,
        allow: Optional[Callable[..., bool]] = None,
        anonymous: bool = False,
        history: Optional[int] = None,
        description: str = "",
        group: Optional[str] = None,
        module: Optional[str] = None,
    ):
        if not (isinstance(event, type) and issubclass(event, BaseModel)):
            raise TopicDeclarationError(f"topic {pattern!r}: event must be a pydantic model class")
        if history is not None and history < 1:
            raise TopicDeclarationError(f"topic {pattern!r}: history must be >= 1")
        self.pattern = pattern
        self.event = event
        self.allow = allow
        self.anonymous = anonymous
        self.history = history
        self.description = description
        self.module = module
        self._group = group
        self.base, self.segments = _parse_pattern(pattern)
        self.params: List[Tuple[str, ParamType]] = [s for s in self.segments if isinstance(s, tuple)]
        if allow is not None:
            _check_allow(pattern, allow, [name for name, _ in self.params])

    # -- names ------------------------------------------------------------------------------------

    @property
    def shape(self) -> Tuple[Any, ...]:
        """Literal parts with every parameter as None: two topics of one shape would shadow each other."""
        return (self.base,) + tuple(None if isinstance(s, tuple) else s for s in self.segments)

    def __call__(self, **params: Any) -> BoundTopic:
        expected = {name for name, _ in self.params}
        if set(params) != expected:
            raise TypeError(f"topic {self.pattern!r} takes {sorted(expected)}, got {sorted(params)}")
        parts = [self.base]
        for seg in self.segments:
            if isinstance(seg, tuple):
                name, kind = seg
                text = str(params[name])
                if not _VALUE_RE[kind].match(text):
                    raise ValueError(f"topic {self.pattern!r}: {name}={text!r} is not a valid {kind} segment")
                parts.append(text)
            else:
                parts.append(seg)
        name = ":".join(parts)
        return BoundTopic(self, name, self._convert(params))

    def match(self, name: str) -> Optional[Dict[str, Any]]:
        """Parameters of a concrete name, or None when it is not this topic."""
        parts = name.split(":")
        if parts[0] != self.base or len(parts) - 1 != len(self.segments):
            return None
        found: Dict[str, Any] = {}
        for seg, text in zip(self.segments, parts[1:]):
            if isinstance(seg, tuple):
                pname, kind = seg
                if not _VALUE_RE[kind].match(text):
                    return None
                found[pname] = int(text) if kind == "int" else text
            elif seg != text:
                return None
        return found

    def _convert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        kinds = dict(self.params)
        return {k: int(v) if kinds[k] == "int" else str(v) for k, v in params.items()}

    # -- permission -------------------------------------------------------------------------------

    def is_allowed(self, user, params: Dict[str, Any]) -> bool:
        """Sync permission check (may hit the ORM). Anonymous users pass only on `anonymous=True` topics."""
        authenticated = bool(getattr(user, "is_authenticated", False))
        if not authenticated and not self.anonymous:
            return False
        if self.allow is None:
            return True
        return bool(self.allow(user, **params))

    # -- metadata ---------------------------------------------------------------------------------

    @property
    def group(self) -> str:
        """OpenAPI tag the topic is sliced by: the short name of the declaring app, unless set."""
        if self._group:
            return self._group
        if self.module:
            try:
                from django.apps import apps

                config = apps.get_containing_app_config(self.module)
            except Exception:  # noqa: BLE001 - apps not ready: fall back to the module path
                config = None
            if config is not None:
                return config.name.split(".")[-1]
            return self.module.split(".")[-2] if "." in self.module else self.module
        return self.base.split(".")[0]

    def __repr__(self) -> str:
        return f"Topic({self.pattern!r}, event={self.event.__name__})"


_SPLIT_RE = re.compile(r":(?![^{]*\})")  # a colon outside {...}: `{order_id:int}` is one segment


def _parse_pattern(pattern: str):
    parts = _SPLIT_RE.split(pattern)
    base, rest = parts[0], parts[1:]
    if not _BASE_RE.match(base):
        raise TopicDeclarationError(f"topic {pattern!r}: the base must match [a-z0-9_.-]+")
    segments: List[Any] = []
    names = set()
    for raw in rest:
        param = _PARAM_RE.match(raw)
        if param:
            name, kind = param.group(1), param.group(2) or "str"
            if name in names:
                raise TopicDeclarationError(f"topic {pattern!r}: parameter {name!r} appears twice")
            names.add(name)
            segments.append((name, kind))
        elif _LITERAL_RE.match(raw):
            segments.append(raw)
        else:
            raise TopicDeclarationError(f"topic {pattern!r}: segment {raw!r} is neither a literal nor {{name}}")
    return base, segments


def _check_allow(pattern: str, allow: Callable[..., bool], params: List[str]) -> None:
    if inspect.iscoroutinefunction(allow):
        raise TopicDeclarationError(f"topic {pattern!r}: allow must be a sync function (it runs in a thread)")
    try:
        inspect.signature(allow).bind(None, **{name: None for name in params})
    except TypeError as exc:
        wanted = ", ".join(["user", *params])
        raise TopicDeclarationError(f"topic {pattern!r}: allow must accept ({wanted}): {exc}") from exc
    except ValueError:
        pass  # no signature (a builtin): trust it


class Registry:
    """Every declared topic of the process. Thread-safe; lookups are by base, then by shape."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_base: Dict[str, List[Topic]] = {}
        self._discovered = False
        self._anonymous: Optional[bool] = None  # cached has_anonymous(); reset on every change

    def register(self, topic: Topic) -> Topic:
        if topic.history is not None:
            from django_cfg.models.django.realtime import REPLAY_MARGIN

            from .backends import get_realtime_config

            limit = get_realtime_config().send_queue - REPLAY_MARGIN
            if topic.history > limit:
                raise TopicDeclarationError(
                    f"topic {topic.pattern!r}: history={topic.history} exceeds send_queue - {REPLAY_MARGIN} "
                    f"({limit}); a full replay has to fit the send queue"
                )
        with self._lock:
            self._anonymous = None
            for other in self._by_base.get(topic.base, []):
                if other.shape == topic.shape:
                    raise TopicDeclarationError(
                        f"topic {topic.pattern!r} shadows {other.pattern!r} (declared in {other.module})"
                    )
            self._by_base.setdefault(topic.base, []).append(topic)
        return topic

    def unregister(self, topic: Topic) -> None:
        with self._lock:
            self._anonymous = None
            items = self._by_base.get(topic.base, [])
            if topic in items:
                items.remove(topic)

    def resolve(self, name: str) -> BoundTopic:
        """Concrete name -> BoundTopic, or UnknownTopic."""
        if not TOPIC_RE.match(name or ""):
            raise UnknownTopic(f"{name!r} is not a topic name")
        self.ensure_discovered()
        for topic in self._by_base.get(name.split(":", 1)[0], []):
            params = topic.match(name)
            if params is not None:
                return BoundTopic(topic, name, params)
        raise UnknownTopic(f"no topic is declared for {name!r}")

    def all(self) -> List[Topic]:
        self.ensure_discovered()
        return sorted((t for items in self._by_base.values() for t in items), key=lambda t: t.pattern)

    def has_anonymous(self) -> bool:
        cached = self._anonymous
        if cached is None or not self._discovered:
            cached = any(t.anonymous for t in self.all())
            if self._discovered:
                self._anonymous = cached
        return cached

    def ensure_discovered(self) -> None:
        """Import every installed app's `realtime` module once, when the app registry is ready."""
        if self._discovered:
            return
        from django.apps import apps

        if not apps.models_ready:  # True inside AppConfig.ready(), where autodiscovery runs first
            return
        self._discovered = True
        from django.utils.module_loading import autodiscover_modules

        autodiscover_modules("realtime")


registry = Registry()


def topic(pattern: str, **options: Any) -> Topic:
    """Declare a topic; see the module docstring. Returns the Topic (call it with parameters for a name)."""
    if "module" not in options:
        frame = inspect.currentframe()
        caller = frame.f_back if frame is not None else None
        options["module"] = caller.f_globals.get("__name__") if caller is not None else None
    return registry.register(Topic(pattern, **options))


__all__ = [
    "BoundTopic", "Hint", "InvalidEvent", "RealtimeError", "Registry", "Topic", "TopicDeclarationError",
    "UnknownTopic", "registry", "topic",
]
