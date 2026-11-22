"""System checks for `config.realtime`.

django_cfg.E050  realtime is enabled outside DEBUG without Redis: the memory backend is per process, so a publish
                 from a worker, an RQ job or another uvicorn worker never reaches the sockets.
django_cfg.E051  realtime.backend="redis" without DjangoConfig.redis_url.
django_cfg.W050  uvicorn below 0.53: no write flow control for slow WebSocket clients (0.52.1) and a keep-alive
                 timer that drops upgraded sockets (0.53.0). Install `django-cfg[realtime]`.
django_cfg.W051  uvicorn is installed without a WebSocket library (`websockets` or `wsproto`): every handshake fails.
django_cfg.W052  an `invalidated_by` topic whose name has neither ':' nor '.': no client cache key can carry it.
"""

from __future__ import annotations

from django.core.checks import Error, Tags, Warning, register

UVICORN_FLOOR = (0, 53)


def _version(dist: str):
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version(dist)
    except PackageNotFoundError:
        return None


def _tuple(text: str):
    parts = []
    for piece in text.split(".")[:2]:
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


def realtime_problems(realtime, *, redis_url, debug: bool, uvicorn=None, ws_libs=None) -> list:
    """The checks as a pure function (tests pass versions instead of reading the environment)."""
    problems = []
    if realtime.backend == "redis" and not redis_url:
        problems.append(Error(
            "realtime.backend is 'redis' but DjangoConfig.redis_url is empty.",
            hint="Set redis_url, or backend='auto'.",
            id="django_cfg.E051",
        ))
    if not realtime.enabled:
        return problems
    in_memory = realtime.backend == "memory" or (realtime.backend == "auto" and not redis_url)
    if in_memory and not debug:
        problems.append(Error(
            "realtime is enabled without Redis: publishes from other processes never reach the sockets.",
            hint="Set DjangoConfig.redis_url (backend='auto' then uses Redis Streams).",
            id="django_cfg.E050",
        ))
    uvicorn = _version("uvicorn") if uvicorn is None else uvicorn
    if uvicorn:
        if _tuple(uvicorn) < UVICORN_FLOOR:
            problems.append(Warning(
                f"uvicorn {uvicorn} is older than 0.53 (WebSocket flow control, keep-alive fix).",
                hint="pip install 'django-cfg[realtime]'",
                id="django_cfg.W050",
            ))
        libs = [lib for lib in ("websockets", "wsproto") if _version(lib)] if ws_libs is None else ws_libs
        if not libs:
            problems.append(Warning(
                "uvicorn has no WebSocket library: every realtime handshake will fail.",
                hint="pip install 'django-cfg[realtime]' (adds websockets)",
                id="django_cfg.W051",
            ))
    return problems


@register(Tags.compatibility)
def check_realtime(app_configs, **kwargs):
    from django.conf import settings

    from django_cfg.core.state.registry import get_current_config
    from django_cfg.modules.django_realtime.backends import get_realtime_config

    config = get_current_config()
    return realtime_problems(
        get_realtime_config(),
        redis_url=getattr(config, "redis_url", None) if config is not None else None,
        debug=bool(settings.DEBUG),
    )


def untaggable_markers(markers) -> list:
    """W052 for each `invalidated_by` topic a cache-key middleware cannot carry: its name has neither ':' nor '.'."""
    return [
        Warning(
            f"{label}: invalidated_by({pattern!r}) cannot tag a cache key",
            hint="The cache-key middleware reads only key parts with ':' or '.' as topics; rename the topic "
                 "(e.g. 'orders.list') or drop the marker.",
            id="django_cfg.W052",
        )
        for label, pattern in markers
        if ":" not in pattern and "." not in pattern
    ]


@register(Tags.urls)
def check_realtime_markers(app_configs, **kwargs):
    from django_cfg.modules.django_realtime.backends import get_realtime_config

    if not get_realtime_config().enabled:
        return []
    from django_cfg.modules.django_realtime.openapi import invalidation_markers

    return untaggable_markers(invalidation_markers())
