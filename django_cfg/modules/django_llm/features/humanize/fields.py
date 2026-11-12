"""Mark a schema field for humanizing; ``tasks.extract`` applies it after parsing.

    class Listing(BaseModel):
        make: str
        description: Annotated[str, Humanize(voice="a dealer writing plainly")]
        highlights: Annotated[list[str], Humanize()]

The marker rides in ``Annotated`` metadata on purpose: it never reaches the JSON
schema sent to the provider (strict ``json_schema`` mode rejects unknown keywords,
and a ``json_schema_extra`` flag would be sent). The rewrite runs AFTER the
structured answer is parsed: a model cannot rewrite its own field mid-generation,
and doing it afterwards keeps the fact guard (``guard.py``) comparing source to rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from .humanizer import Ask, HumanizeResult, humanize


@dataclass(frozen=True)
class Humanize:
    """Field marker. Unset options fall back to the call's / the method's defaults."""

    voice: str | None = None
    domain: str | None = None
    strength: str | None = None
    lang: str | None = None
    keep: tuple[str, ...] = ()


def _marker(info: Any) -> Humanize | None:
    for meta in getattr(info, "metadata", ()):
        if isinstance(meta, Humanize):
            return meta
    return None


def has_marked_fields(schema: type[BaseModel], _seen: set | None = None) -> bool:
    """True when ``schema`` or any nested model declares a ``Humanize`` field."""
    seen = _seen if _seen is not None else set()
    if schema in seen:
        return False
    seen.add(schema)
    for info in schema.model_fields.values():
        if _marker(info):
            return True
        for sub in _nested_models(info.annotation):
            if has_marked_fields(sub, seen):
                return True
    return False


def _nested_models(annotation: Any) -> list[type[BaseModel]]:
    out: list[type[BaseModel]] = []
    stack = [annotation]
    while stack:
        a = stack.pop()
        if isinstance(a, type) and issubclass(a, BaseModel):
            out.append(a)
        stack.extend(getattr(a, "__args__", ()) or ())
    return out


def apply(
    instance: BaseModel,
    ask: Ask,
    *,
    path: str = "",
    defaults: dict[str, Any] | None = None,
    results: dict[str, HumanizeResult] | None = None,
    on_error: Callable[[str, Exception], None] | None = None,
) -> tuple[BaseModel, dict[str, HumanizeResult]]:
    """Return a copy of ``instance`` with marked string fields rewritten, plus a result per field path.

    A failure on one field (transport error) leaves that field as parsed and is reported
    through ``on_error``; one bad field never fails the whole extraction.
    """
    defaults = defaults or {}
    results = results if results is not None else {}
    updates: dict[str, Any] = {}

    def run(value: str, mark: Humanize, where: str) -> str:
        if not isinstance(value, str) or not value.strip():
            return value
        opts = {k: v for k, v in defaults.items() if v is not None}
        for k in ("voice", "domain", "strength", "lang"):
            if getattr(mark, k) is not None:
                opts[k] = getattr(mark, k)
        try:
            res = humanize(value, ask, keep=mark.keep, **opts)
        except Exception as exc:  # noqa: BLE001 - keep the parsed value
            if on_error:
                on_error(where, exc)
            return value
        results[where] = res
        return res.text

    for name, info in type(instance).model_fields.items():
        value = getattr(instance, name)
        where = f"{path}.{name}" if path else name
        mark = _marker(info)
        if mark and isinstance(value, str):
            updates[name] = run(value, mark, where)
        elif mark and isinstance(value, (list, tuple)):
            updates[name] = type(value)(run(v, mark, f"{where}[{i}]") for i, v in enumerate(value))
        elif isinstance(value, BaseModel):
            updates[name] = apply(value, ask, path=where, defaults=defaults, results=results, on_error=on_error)[0]
        elif isinstance(value, (list, tuple)) and value and isinstance(value[0], BaseModel):
            updates[name] = type(value)(
                apply(v, ask, path=f"{where}[{i}]", defaults=defaults, results=results, on_error=on_error)[0]
                for i, v in enumerate(value)
            )
    return (instance.model_copy(update=updates) if updates else instance), results
