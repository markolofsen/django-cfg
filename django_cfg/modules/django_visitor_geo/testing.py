"""Fixed geography for tests: `with override_geo(country="GE"):` or `@override_geo(country="GE")`.

A test client's `HTTP_CF_IPCOUNTRY` from 127.0.0.1 is not trusted (it is not a Cloudflare address), so tests name the
geography they need here instead. Works as a context manager and a decorator, sync and async.
"""

from __future__ import annotations

import functools
import inspect
from contextlib import contextmanager
from typing import Any

from .countries import continent_of
from .geo import FIELD_NAMES, Geo, _override


@contextmanager
def _activate(geo: Geo):
    token = _override.set(geo)
    try:
        yield geo
    finally:
        _override.reset(token)


class override_geo:  # noqa: N801 - reads like Django's override_settings
    def __init__(self, country: str = "", **fields: Any):
        unknown = set(fields) - set(FIELD_NAMES)
        if unknown:
            raise TypeError(f"override_geo: unknown fields {sorted(unknown)}")
        country = country.upper()
        fields.setdefault("continent", continent_of(country))
        fields.setdefault("source", "override")
        fields.setdefault("trusted", True)
        self.geo = Geo(country=country, **fields)
        self._cm = None

    def __enter__(self) -> Geo:
        self._cm = _activate(self.geo)
        return self._cm.__enter__()

    def __exit__(self, *exc):
        return self._cm.__exit__(*exc)

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with _activate(self.geo):
                    return await func(*args, **kwargs)
            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with _activate(self.geo):
                return func(*args, **kwargs)
        return wrapper
