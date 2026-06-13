"""Bounded-concurrency fan-out for image-edit requests.

The headline async win: feed a batch of :class:`ImageEditRequest`
objects through one or many ``ImageEditClient.aedit`` calls
concurrently, capped by ``max_at_once`` so we don't fan past the
provider's rate limit or saturate the worker pool.

Why this exists separately from :mod:`.client`
----------------------------------------------
``ImageEditClient.aedit`` is a per-call async twin. The fan-out is
a different concern (batch orchestration, rate budgeting) that we
want to test and reason about in isolation. Same split the chat
side makes between ``aextract`` and ``extract_many``.

Built on aiometer — same dependency the chat fan-outs already use.
"""

from __future__ import annotations

import functools
from typing import Sequence

from .client import ImageEditClient
from .models import ImageEditRequest, ImageEditResponse


async def edit_many(
    requests: Sequence[ImageEditRequest],
    *,
    client: ImageEditClient | None = None,
    auto_compress: bool = True,
    max_at_once: int = 4,
    max_per_second: float | None = None,
) -> list[ImageEditResponse]:
    """Run many image-edit requests concurrently.

    Parameters
    ----------
    requests
        Pre-built :class:`ImageEditRequest` objects. Order is
        preserved in the result list.
    client
        Optional pre-configured ``ImageEditClient``. Pass one to
        share a connection pool / app-attribution headers across
        the batch, or omit to spin up a default client (uses the
        OpenRouter key from ``get_api_keys()``).
    auto_compress
        Passed through to each :meth:`ImageEditClient.aedit` call —
        see its docstring.
    max_at_once
        Hard cap on in-flight calls. Default 4 — image-edit calls
        run 5-30 s wall-clock; 4 concurrent is enough to amortise
        latency without sprinting past Nano Banana's rate limits
        on a single OpenRouter key. Tune up only if you've
        verified provider headroom.
    max_per_second
        Optional spawn-rate cap, for keys with a stricter RPM
        budget. Aiometer staggers starts to respect it.

    Raises
    ------
    The first per-item exception propagates and cancels the rest
    (aiometer's all-or-nothing default — matches ``extract_many``).
    If you need partial results, wrap each request in a coroutine
    that catches its own errors and pass the results through
    yourself.
    """
    import aiometer  # local — only the fan-out path needs it

    edit_client = client or ImageEditClient()

    async def _one(req: ImageEditRequest) -> ImageEditResponse:
        return await edit_client.aedit(req, auto_compress=auto_compress)

    return await aiometer.run_all(
        [functools.partial(_one, r) for r in requests],
        max_at_once=max_at_once,
        max_per_second=max_per_second,
    )


__all__ = ["edit_many"]
