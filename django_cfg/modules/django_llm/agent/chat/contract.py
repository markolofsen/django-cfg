"""The signature contract of `ChatService`'s protected methods, checked when a subclass is defined.

The kit's views call `service.begin(...)`, `frames`, `attach`, `cancel` and the service calls `after_answer`. A host
override that drops a parameter of the base method fails at the first request (the gptkino `begin` without `attachments`
was a 500 on every send). `check_override` runs from `ChatService.__init_subclass__`, so the same mistake fails at import.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

PROTECTED = ("begin", "frames", "attach", "cancel", "after_answer")

_POSITIONAL = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)


class ChatServiceContractError(TypeError):
    """A `ChatService` subclass overrides a protected method with a signature the framework cannot call."""


def _without_self(sig: inspect.Signature) -> inspect.Signature:
    return sig.replace(parameters=list(sig.parameters.values())[1:])


def problems(base: Callable[..., Any], override: Callable[..., Any]) -> list[str]:
    """What the override cannot accept that the base accepts; empty when every call to the base also fits the override."""
    base_sig, new_sig = _without_self(inspect.signature(base)), _without_self(inspect.signature(override))
    has_args = any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in new_sig.parameters.values())
    has_kwargs = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in new_sig.parameters.values())
    mine = new_sig.parameters
    mine_positional = [p.name for p in mine.values() if p.kind in _POSITIONAL]
    found: list[str] = []
    for index, p in enumerate(q for q in base_sig.parameters.values() if q.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)):
        if p.kind in _POSITIONAL:
            # Callers pass these by position, so `**kwargs` cannot stand in for them: the name must be kept in the same place.
            if index >= len(mine_positional) or mine_positional[index] != p.name:
                where = "moved" if p.name in mine else "dropped"
                found.append(f"{where} the positional parameter {p.name!r} (position {index + 1})")
        elif p.name not in mine and not has_kwargs:
            found.append(f"dropped the keyword parameter {p.name!r} (add it, or take **kwargs and forward it)")
    base_names = set(base_sig.parameters)
    for p in mine.values():
        if p.name not in base_names and p.default is inspect.Parameter.empty and p.kind in (*_POSITIONAL, inspect.Parameter.KEYWORD_ONLY):
            found.append(f"added the required parameter {p.name!r} that no caller passes")
    if inspect.iscoroutinefunction(base) != inspect.iscoroutinefunction(override):
        found.append("changed between `def` and `async def`")
    if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in base_sig.parameters.values()) and not has_args:
        found.append("dropped *args")
    return found


def check_subclass(cls: type, base: type) -> None:
    """Raise `ChatServiceContractError` for the first protected method `cls` defines with a signature that drops the base's."""
    for name in PROTECTED:
        override = cls.__dict__.get(name)
        if override is None:
            continue
        func = override.__func__ if isinstance(override, (staticmethod, classmethod)) else override
        if not callable(func):
            raise ChatServiceContractError(f"{cls.__qualname__}.{name} must be a method")
        found = problems(getattr(base, name), func)
        if found:
            raise ChatServiceContractError(
                f"{cls.__module__}.{cls.__qualname__}.{name}() cannot be called the way the framework calls {base.__name__}.{name}(): "
                + "; ".join(found)
                + f". Do not subclass {base.__name__} for host data: use a ChatKind hook (docs: agent/chat/@docs/extending.md)."
            )
