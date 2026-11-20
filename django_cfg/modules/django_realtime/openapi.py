"""drf-spectacular postprocessing hook: the topic registry as `x-realtime` in the OpenAPI document.

    "x-realtime": {"version": 1, "path": "/ws", "topics": [
        {"name": "orders:{order_id}", "params": [{"name": "order_id", "type": "int"}], "anonymous": false,
         "history": 100, "event": {"$ref": "#/components/schemas/OrderEvent"}, "tags": ["orders"],
         "description": ""}]}

Event models (and their nested models) become ordinary `components.schemas`, so the generator emits zod for them
and slices them per group by `tags` like operations. A name that already holds a different schema is a collision
and stops generation; it is never overwritten.

`@invalidated_by("orders:{order_id}")` on a DRF view, viewset or action marks the operations whose responses the
topic invalidates. The schema class writes it as `x-realtime-invalidates` on each operation; the generator tags the
SWR keys of those reads with the concrete topic name, the parameters taken from the path parameters of the same
names. A marker naming no declared topic stops generation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple, TypeVar

from .protocol import PROTOCOL_VERSION

REF_TEMPLATE = "#/components/schemas/{model}"
#: The operation extension, and the view attribute the schema class reads it from (django_generator's
#: PathBasedAutoSchema; the generator cannot import this module, so the two names are spelled there too).
INVALIDATES = "x-realtime-invalidates"
MARKER_ATTR = "realtime_invalidates"

F = TypeVar("F", bound=Callable[..., Any])


def invalidated_by(*patterns: str) -> Callable[[F], F]:
    """Mark a DRF view class, viewset, action or `@api_view` function as invalidated by these topic patterns.

    Stack it on an action or a view; markers on the action and on its class add up.
    """
    from .registry import Topic

    if not patterns:
        raise TypeError("invalidated_by() needs at least one topic pattern")
    for pattern in patterns:
        Topic(pattern)  # the pattern syntax, now; the topic itself at schema generation

    def decorator(obj: F) -> F:
        target = getattr(obj, "cls", obj)  # @api_view returns a function holding the view class
        current = list(target.__dict__.get(MARKER_ATTR, ())) if isinstance(target, type) else \
            list(getattr(target, MARKER_ATTR, ()))
        setattr(target, MARKER_ATTR, tuple(dict.fromkeys(current + list(patterns))))
        return obj

    return decorator


class SchemaCollision(Exception):
    pass


def _put(schemas: Dict[str, Any], name: str, schema: Dict[str, Any], pattern: str) -> None:
    existing = schemas.get(name)
    if existing is not None and existing != schema:
        raise SchemaCollision(
            f"realtime topic {pattern!r}: components.schemas[{name!r}] already holds a different schema; "
            "rename the event model (or its nested model)"
        )
    schemas[name] = schema


def realtime_document(result: Dict[str, Any]) -> Dict[str, Any]:
    from .backends import get_realtime_config
    from .registry import registry

    topics = registry.all()
    if not topics:
        return result
    schemas = result.setdefault("components", {}).setdefault("schemas", {})
    entries = []
    for topic in topics:
        schema = topic.event.model_json_schema(ref_template=REF_TEMPLATE)
        for name, nested in (schema.pop("$defs", None) or {}).items():
            _put(schemas, name, nested, topic.pattern)
        title = topic.event.model_config.get("title") or ""
        name = title if title.isidentifier() else topic.event.__name__
        _put(schemas, name, schema, topic.pattern)
        entries.append({
            "name": topic.pattern,
            "params": [{"name": p, "type": kind} for p, kind in topic.params],
            "anonymous": topic.anonymous,
            "history": topic.history or get_realtime_config().default_history,
            "event": {"$ref": REF_TEMPLATE.format(model=name)},
            "tags": [topic.group],
            "description": topic.description,
        })
    result["x-realtime"] = {"version": PROTOCOL_VERSION, "path": get_realtime_config().path, "topics": entries}
    return result


def invalidation_markers(urlconf: Any = None) -> List[Tuple[str, str]]:
    """(view label, pattern) for every `invalidated_by` marker reachable from the URLconf."""
    from django.urls import URLPattern, URLResolver, get_resolver

    found: Dict[Tuple[str, str], None] = {}

    def visit(patterns) -> None:
        for entry in patterns:
            if isinstance(entry, URLResolver):
                visit(entry.url_patterns)
            elif isinstance(entry, URLPattern):
                cls = getattr(entry.callback, "cls", None)
                if cls is None:
                    continue
                handlers = list((getattr(entry.callback, "actions", None) or {}).values()) or \
                    [m for m in ("get", "post", "put", "patch", "delete") if hasattr(cls, m)]
                label = f"{cls.__module__}.{cls.__qualname__}"
                for source in [cls] + [getattr(cls, h, None) for h in handlers]:
                    for pattern in getattr(source, MARKER_ATTR, ()) or ():
                        found[(label, pattern)] = None

    visit(get_resolver(urlconf).url_patterns)
    return list(found)


def check_invalidations(result: Dict[str, Any]) -> List[str]:
    """Every `x-realtime-invalidates` pattern must have the shape of a declared topic; UnknownTopic otherwise."""
    from .registry import Topic, UnknownTopic, registry

    shapes = {t.shape for t in registry.all()}
    seen: List[str] = []
    for path, item in (result.get("paths") or {}).items():
        for method, operation in (item or {}).items():
            if not isinstance(operation, dict):
                continue
            for pattern in operation.get(INVALIDATES) or ():
                if Topic(pattern).shape not in shapes:
                    raise UnknownTopic(
                        f"{method.upper()} {path}: invalidated_by({pattern!r}) names no declared topic"
                    )
                seen.append(pattern)
    return seen


def postprocess_realtime(result, generator, request, public):  # noqa: ARG001 - drf-spectacular hook signature
    check_invalidations(result)
    return realtime_document(result)


__all__ = ["INVALIDATES", "MARKER_ATTR", "SchemaCollision", "check_invalidations", "invalidated_by",
           "invalidation_markers",
           "postprocess_realtime", "realtime_document"]
