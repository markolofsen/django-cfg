"""Follow an answer from storage: what a second tab or a reconnect receives instead of (or after) the live stream.

The live stream and this one carry the same frames, and each frame keeps the `id:` it had in the run (the stream position the driver
stamped), so a client resumes from the last id it saw whichever stream gave it. Two things have no id: the text (it is one growing
string, so the client says how much of it it holds, `text_offset`, in UTF-16 code units as a JS `string.length`) and the frames that
are not positions in the run (`run`, `done`, `error`).

Order: `run` (with `resume: true`), the text past the offset, the steps and parts past `after` by their stamp, then the closing
frame once the row is closed. A `cancelled` row ends with no closing frame, as the live stream does.

`Tailer` is pure: give it the row as it stands, it returns the frames not yet sent. `follow` is the polling loop around it.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass

from django_cfg.modules.django_llm.agent.bus.events import (
    PING,
    DoneEvent,
    ErrorEvent,
    RunEvent,
    TextDeltaEvent,
    TraceStepEvent,
    UIPayloadEvent,
    encode_sse,
)
from django_cfg.modules.django_llm.agent.chat.turn import Progress, Status
from django_cfg.modules.django_llm.agent.runtime.errors import DEFAULT_ERROR_MESSAGES
from django_cfg.modules.django_llm.agent.trace.resume import UNSTAMPED, steps_after


@dataclass(frozen=True)
class Cursor:
    """Where a reader already is: the last stream position it saw, and how much of the text it holds."""

    after: int = 0
    text_offset: int = 0  # UTF-16 code units, what JavaScript's `string.length` counts


def utf16_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def utf16_tail(text: str, offset: int) -> str:
    """`text` from UTF-16 code unit `offset` on. An offset inside a surrogate pair (a client that cut one) drops the broken half."""
    return text.encode("utf-16-le")[2 * max(0, offset):].decode("utf-16-le", errors="ignore")


class Tailer:
    def __init__(self, run: RunEvent, cursor: Cursor, level: int) -> None:
        self._run = run
        self._level = level
        self._after = cursor.after
        self._text_pos = cursor.text_offset
        self._run_sent = False
        self._unstamped: dict[str, str] = {}  # what was sent without an id, by step id or part index: not sent again unchanged

    def advance(self, row: Progress) -> tuple[list[str], bool]:
        """The frames the row holds beyond what this tailer sent, and whether the row is closed (nothing follows)."""
        out: list[str] = []
        if not self._run_sent:
            self._run_sent = True
            out.append(encode_sse(RunEvent(thread_id=self._run.thread_id, message_id=self._run.message_id, client_id=self._run.client_id, seq=self._run.seq, resume=True), "widget") or "")
        new_text = utf16_tail(row.text, self._text_pos)
        if new_text:
            self._text_pos += utf16_len(new_text)
            out.append(encode_sse(TextDeltaEvent(delta=new_text), "widget") or "")

        items: list[tuple[int, str, object]] = []
        for stamp, step in steps_after(row.trace, self._level, self._after):
            items.append((stamp, f"step:{step.get('step_id')}", step))
        for index, part in enumerate(row.parts):
            if not isinstance(part, dict) or "kind" not in part:
                continue
            stamp = part.get("event_seq")
            if stamp is None:
                items.append((UNSTAMPED, f"part:{index}", part))
            elif stamp > self._after:
                items.append((stamp, f"part:{index}", part))
        items.sort(key=lambda item: item[0])
        for stamp, key, body in items:
            stamped = stamp != UNSTAMPED
            if not stamped:
                signature = json.dumps(body, sort_keys=True, default=str)
                if self._unstamped.get(key) == signature:
                    continue
                self._unstamped[key] = signature
            event = (
                TraceStepEvent(step=body, event_seq=stamp if stamped else None)  # type: ignore[arg-type]
                if key.startswith("step:")
                else UIPayloadEvent(kind=body["kind"], data=body.get("data"))  # type: ignore[index, union-attr]
            )
            out.append(encode_sse(event, "widget", seq=stamp if stamped else None) or "")
            if stamped:
                self._after = max(self._after, stamp)

        if row.status is Status.RUNNING:
            return out, False
        if row.status is Status.DONE:
            out.append(encode_sse(DoneEvent(tokens_input=row.tokens_in, tokens_output=row.tokens_out, cost_usd=row.cost_usd, finish_reason="stop"), "widget") or "")
        elif row.status is Status.ERROR:
            code = row.error_code if row.error_code in DEFAULT_ERROR_MESSAGES else "failed"
            out.append(encode_sse(ErrorEvent(error=DEFAULT_ERROR_MESSAGES[code], code=code, retryable=True), "widget") or "")
        return out, True  # cancelled: no closing frame


async def follow(
    read: Callable[[], Progress | None],
    tailer: Tailer,
    *,
    poll_s: float,
    ping_s: float,
    is_stale: Callable[[Progress], bool],
    reap: Callable[[], None],
) -> AsyncIterator[str]:
    """Poll the row and send what is new until it closes. `read`, `reap` are sync (ORM); a row stale past its window is closed by `reap` and read once more."""
    from asgiref.sync import sync_to_async

    read_row = sync_to_async(read)
    last_sent = time.monotonic()
    while True:
        row = await read_row()
        if row is None:
            return
        if row.status is Status.RUNNING and is_stale(row):
            await sync_to_async(reap)()
            row = await read_row()
            if row is None:
                return
        chunks, finished = tailer.advance(row)
        for chunk in chunks:
            last_sent = time.monotonic()
            yield chunk
        if finished:
            return
        await asyncio.sleep(poll_s)
        if time.monotonic() - last_sent >= ping_s:
            last_sent = time.monotonic()
            yield PING
