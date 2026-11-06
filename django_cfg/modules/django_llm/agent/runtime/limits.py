"""Per-run limits for the agent loop: configurable, with the historical default.

`stream_agent_run` used to hard-code ``UsageLimits(request_limit=15)``. The default is
unchanged; what changed is that it can be set, from most to least specific:

1. the ``limits=`` argument of ``stream_agent_run``;
2. ``deps.run_limits`` (a ``RunLimits`` or a plain dict; ``AgentDeps`` has the field);
3. the process-wide default, ``set_default_run_limits(...)``, which a host calls once
   from its ``AppConfig.ready()`` or settings module (the plane itself never reads
   Django settings: ``_integration.py`` is the only seam);
4. ``RunLimits()``: ``request_limit=15``, nothing else.

``None`` for a field means "no limit" for that field (``request_limit=None`` removes the
cap; do not, outside tests).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any

#: The historical hard-coded cap on model round-trips in one run.
DEFAULT_REQUEST_LIMIT = 15


@dataclass(frozen=True)
class RunLimits:
    """The pydantic-ai ``UsageLimits`` fields a host may reasonably set."""

    request_limit: int | None = DEFAULT_REQUEST_LIMIT
    tool_calls_limit: int | None = None
    input_tokens_limit: int | None = None
    output_tokens_limit: int | None = None
    total_tokens_limit: int | None = None
    per_request_input_tokens_limit: int | None = None

    @classmethod
    def coerce(cls, value: Any) -> RunLimits:
        """``RunLimits`` from a ``RunLimits``, a mapping of its fields, or ``None`` (the defaults).

        An unknown key raises ``TypeError``: a typo in a limit must not silently run unlimited.
        """
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            known = {f.name for f in fields(cls)}
            unknown = set(value) - known
            if unknown:
                raise TypeError(f"unknown run limit(s): {sorted(unknown)}; known: {sorted(known)}")
            return cls(**value)
        raise TypeError(f"run limits must be RunLimits, a mapping or None, not {type(value).__name__}")

    def to_usage_limits(self) -> Any:
        """The pydantic-ai ``UsageLimits`` for this run."""
        from pydantic_ai import UsageLimits

        return UsageLimits(**{f.name: getattr(self, f.name) for f in fields(self)})


_default: RunLimits | None = None


def set_default_run_limits(value: Any) -> RunLimits | None:
    """Set (or, with ``None``, clear) the process-wide default. Returns the previous one."""
    global _default
    previous = _default
    _default = None if value is None else RunLimits.coerce(value)
    return previous


def get_default_run_limits() -> RunLimits:
    return _default if _default is not None else RunLimits()


def resolve_run_limits(explicit: Any = None, deps: Any = None) -> RunLimits:
    """The limits for a run: argument, then ``deps.run_limits``, then the process default."""
    if explicit is not None:
        return RunLimits.coerce(explicit)
    on_deps = getattr(deps, "run_limits", None)
    if on_deps is not None:
        return RunLimits.coerce(on_deps)
    return get_default_run_limits()
