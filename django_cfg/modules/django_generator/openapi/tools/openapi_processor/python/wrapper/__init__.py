"""Python wrapper generator.

Reads an openapi-python-client output tree and emits a thin convenience
class per tag-group:

    out_dir/<tag>/api.py        ← class <Tag>API (generated)

Each ``<Tag>API`` exposes:

* ``__init__(base_url, token=None, api_key=None, timeout=None)`` — picks
  ``Client`` or ``AuthenticatedClient`` and injects ``x-api-key`` via
  ``httpx_args`` when ``api_key`` is supplied.
* one method per operation, name = operation function file name with
  the leading ``<tag>_`` prefix stripped, body delegated to
  ``<op>.asyncio(client=self._client, **kwargs)``.
* ``async with`` context manager support.

The wrapper is regenerated on every ``make gen`` from the freshly
written operation files (no shared state with the prior pass).
"""

from .generator import generate

__all__ = ["generate"]
