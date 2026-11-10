"""Which steps of a stored trace a reader that already holds the stream up to position `after` still needs.

The driver stamps every trace frame with its stream position and the recorder keeps the newest stamp of each step in
`TraceDoc.frames`. A resume compares them with the id the client last saw. A step without a stamp (a frame published but not yet
sent when the document was stored) is always sent: a step is an upsert on the client, so a repeat costs nothing and a miss would.
"""

from __future__ import annotations

import logging
from typing import Any

from django_cfg.modules.django_llm.agent.trace.recorder import step_wire
from django_cfg.modules.django_llm.agent.trace.redact import Redactor, shape_step
from django_cfg.modules.django_llm.agent.trace.step import TraceDoc

log = logging.getLogger(__name__)

UNSTAMPED = 1 << 62  # sorts after every stamped frame


def steps_after(doc: dict | None, level: int, after: int, redactor: Redactor | None = None) -> list[tuple[int, dict[str, Any]]]:
    """`(stamp, wire step)` for each step of `doc` past `after`, oldest first, shaped for a reader at `level`.

    An unstamped step carries `UNSTAMPED`; the caller sends it without an `id:` so the client's resume position does not jump over frames
    that are still to come.
    """
    if not doc or level <= 0:
        return []
    try:
        parsed = TraceDoc.model_validate(doc)
    except Exception:  # noqa: BLE001 - a stored value this code cannot read is not shown
        log.warning("trace: a stored trace does not parse; nothing resumed")
        return []
    effective = min(level, parsed.level) if parsed.level else 0
    if effective <= 0:
        return []
    out: list[tuple[int, dict[str, Any]]] = []
    for step in parsed.steps:
        stamp = parsed.frames.get(step.step_id, UNSTAMPED)
        if stamp > after:
            out.append((stamp, step_wire(shape_step(step, effective, redactor))))
    out.sort(key=lambda pair: pair[0])
    return out
