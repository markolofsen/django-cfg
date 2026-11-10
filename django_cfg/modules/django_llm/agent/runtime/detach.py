"""Let a run outlive its reader: pump the frames in a task of its own and hand them to whoever is still listening.

Without this, closing the connection cancels the generator that drives the run (the run is stored `cancelled`, what was said kept).
With it the run goes on to its end, is stored `done`, and later readers find it in storage (`GET .../stream`). It is opt-in per
kind (`ChatKind.detach`): a run that keeps spending after the user left must be a decision of the kind, not a side effect.

The pump task is held here, so it is not collected, and it ends with the run (the driver's own wall-clock cap, `timeout_s`).
Chunks produced after the reader left are dropped: nobody is there, and storage has them. It needs an event loop that outlives the
request: an ASGI server. Under WSGI Django runs the stream on a loop that closes with the response, and the run ends with it.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

log = logging.getLogger(__name__)

_PUMPS: set[asyncio.Task] = set()
_END = object()


async def detached(frames: AsyncIterator[str]) -> AsyncIterator[str]:
    queue: asyncio.Queue = asyncio.Queue()
    attached = True

    async def pump() -> None:
        try:
            async for chunk in frames:
                if attached:
                    queue.put_nowait(chunk)
        except Exception as exc:  # noqa: BLE001 - the driver turns a run failure into frames; this is a bug in the stream itself
            if attached:
                queue.put_nowait(exc)
            else:
                log.exception("detached run: the stream failed after its reader left")
        finally:
            queue.put_nowait(_END)

    task = asyncio.ensure_future(pump())
    _PUMPS.add(task)
    task.add_done_callback(_PUMPS.discard)
    try:
        while True:
            item = await queue.get()
            if item is _END:
                return
            if isinstance(item, Exception):
                raise item
            yield item
    finally:
        attached = False  # the reader is gone (closed, cancelled, or done): the pump keeps the run going on its own
