"""Topic tags for SWR keys, from an operation's ``x-realtime-invalidates``.

A key is tagged with a topic when it holds the concrete topic name as one of its elements
(``["orders_retrieve", args, "orders:42"]``); the host's SWR middleware subscribes tagged keys and revalidates
them on each message, so nothing generated here imports the realtime client. A pattern parameter comes from the
path parameter of the same name. Left out, with a warning: a topic with a parameter the call cannot supply, and a
topic whose name holds neither ':' nor '.' (the middleware reads only such key parts as topics, so a plain part
like "me" never opens a subscription).
"""

from __future__ import annotations

import json
import logging

from ..ir import IROperation
from ..topic_patterns import PARAM_RE, SPLIT_RE

_log = logging.getLogger(__name__)


def topic_tag_exprs(op: IROperation, args: str = "args", *, warn: bool = True) -> list[str]:
    """TS expressions, one per resolvable topic, evaluating to the concrete topic name for this call."""
    path_names = {p.name for p in op.path_params}
    exprs: list[str] = []
    for pattern in op.realtime_invalidates:
        parts = SPLIT_RE.split(pattern)
        if len(parts) == 1 and "." not in parts[0]:
            if warn:
                _log.warning(
                    "%s (%s %s): x-realtime-invalidates %r is not tagged: a topic key part needs ':' or '.'",
                    op.operation_id, op.method.upper(), op.path, pattern,
                )
            continue
        out = [parts[0]]  # literals are [a-z0-9_.-] (django_realtime validates patterns)
        missing = []
        for raw in parts[1:]:
            match = PARAM_RE.match(raw)
            if match is None:
                out.append(raw)
            elif match.group(1) in path_names:
                out.append("${String(%s.path[%s])}" % (args, json.dumps(match.group(1))))
            else:
                missing.append(match.group(1))
        if missing and warn:
            _log.warning(
                "%s (%s %s): x-realtime-invalidates %r is not tagged: no path parameter %s",
                op.operation_id, op.method.upper(), op.path, pattern, ", ".join(missing),
            )
        if missing:
            continue
        text = ":".join(out)
        exprs.append(f"`{text}`" if "${" in text else json.dumps(text))
    return list(dict.fromkeys(exprs))


def tag_suffix(op: IROperation, args: str = "args", *, warn: bool = True) -> str:
    """``, "orders.all", `orders:${...}``` for splicing into a key array literal, or ``""``."""
    exprs = topic_tag_exprs(op, args, warn=warn)
    return "".join(", " + e for e in exprs)


__all__ = ["tag_suffix", "topic_tag_exprs"]
