"""``x-realtime-invalidates`` on React Query: the topics a generated query tags itself with (H2.10).

An operation marked ``@invalidated_by("orders:{order_id}")`` must refetch when that topic publishes. Orval carries the
fact into the generated hooks through its per-operation ``query.queryOptions`` mutator: Python sets
``override.operations[<operationId>].query.queryOptions`` on exactly the GET operations that carry the extension, and
points it at ``runtime/realtime-query.ts``, written here. Orval calls the mutator with the query options, the call's
own arguments (``{ id }``, ``{ params }``) and ``{ url, operationId, operationName }``; the mutator adds the concrete
topic names to ``meta.realtimeTopics`` and keeps the caller's ``meta``. ``@djangocfg/layouts`` watches the QueryCache
and keeps those topics subscribed while such a query has observers, so a page needs no code.

Why this and not the alternatives (Orval 8.48.0):

* a map beside ``realtime.ts`` needs every app to hand each generated group's map to the layout, and a query key
  holds the path with its parameters already filled in, so the runtime would have to match route templates;
* ``override.query.options`` is deprecated in 8.x and is a static literal: it cannot read a path parameter;
* a global ``queryOptions`` mutator would rewrite every query of every group; per operation, untagged operations stay
  byte-identical.

A ``{param}`` resolves from the path parameter of the same name, read from the call's arguments under Orval's name
for it. A pattern parameter that is no path parameter of the operation stops generation, named: a list cannot know
which ``order_id`` to watch. Non-GET operations are skipped: they have no query (``invalidated_by`` on a viewset marks
its writes too).
"""

from __future__ import annotations

import json
import re
from typing import Any

from .topic_patterns import split_pattern

REALTIME_QUERY_FILE = "realtime-query.ts"
REALTIME_QUERY_EXPORT = "realtimeQueryOptions"
INVALIDATES = "x-realtime-invalidates"
#: The ``meta`` key ``@djangocfg/layouts`` reads. Concrete topic names, never patterns.
META_KEY = "realtimeTopics"

_WORD_RE = re.compile(r"[^A-Za-z0-9]+")


class RealtimeInvalidationError(ValueError):
    pass


def _orval_prop(name: str) -> str:
    """Orval's argument name for a path parameter: lower camel case (``user_id`` -> ``userId``)."""
    head, *rest = [p for p in _WORD_RE.split(name) if p] or [name]
    return head[:1].lower() + head[1:] + "".join(p[:1].upper() + p[1:] for p in rest)


def invalidating_queries(document: dict[str, Any]) -> dict[str, list[str]]:
    """``{operationId: [pattern, ...]}`` for every GET operation that carries ``x-realtime-invalidates``.

    Raises ``RealtimeInvalidationError`` for a pattern parameter that is not a path parameter of the operation.
    """
    out: dict[str, list[str]] = {}
    for path, item in (document.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        op = item.get("get")
        if not isinstance(op, dict) or not op.get(INVALIDATES) or not op.get("operationId"):
            continue
        path_params = {
            str(p.get("name"))
            for p in [*(item.get("parameters") or []), *(op.get("parameters") or [])]
            if isinstance(p, dict) and p.get("in") == "path"
        }
        patterns = [str(p) for p in op[INVALIDATES]]
        for pattern in patterns:
            missing = [name for name, kind in split_pattern(pattern)[1] if kind and name not in path_params]
            if missing:
                raise RealtimeInvalidationError(
                    f"GET {path} ({op['operationId']}): invalidated_by({pattern!r}) needs "
                    f"{', '.join(missing)}, which is no path parameter of this operation "
                    f"(path parameters: {', '.join(sorted(path_params)) or 'none'}). A query refetches on the topic "
                    "it can name: mark this view with a topic it can fill from its own path, or a broader topic "
                    "without the parameter"
                )
        out[str(op["operationId"])] = list(dict.fromkeys(patterns))
    return dict(sorted(out.items()))


def _topic_expr(pattern: str) -> tuple[str, list[str]]:
    """``(TS expression of the concrete name, Orval argument names it reads)``."""
    base, segments = split_pattern(pattern)
    props = [_orval_prop(name) for name, kind in segments if kind]
    if not props:
        return json.dumps(pattern), []
    parts = [base]
    for name, kind in segments:
        parts.append(name if kind is None else f"${{String(props[{json.dumps(_orval_prop(name))}])}}")
    template = "`" + ":".join(parts) + "`"
    return f"filled(props, {', '.join(json.dumps(p) for p in props)}) ? {template} : null", props


def _entry(op: str, patterns: list[str]) -> str:
    exprs = [_topic_expr(p) for p in patterns]
    arg = "props" if any(props for _, props in exprs) else ""
    return f"  {json.dumps(op)}: ({arg}) => [{', '.join(e for e, _ in exprs)}],"


_HEADER = """// AUTO-GENERATED by django_cfg: do not edit, re-run `make gen`.
// Orval's `queryOptions` mutator for the operations marked `invalidated_by` (`x-realtime-invalidates`).
// It adds the concrete topic names to `meta.%(meta)s`; `@djangocfg/layouts` keeps those topics subscribed
// while the query has observers and invalidates it on each message or gap.

type QueryOptionsWithMeta = { meta?: Record<string, unknown> };
type OperationRef = { url: string; operationId: string; operationName: string };
"""

_FILLED = """
/** A topic with a path parameter is watched only once the query has that parameter (a disabled query may not). */
function filled(props: Record<string, unknown>, ...names: string[]): boolean {
  return names.every((name) => props[name] !== undefined && props[name] !== null && props[name] !== '');
}
"""


def render_realtime_query(queries: dict[str, list[str]]) -> str:
    """The text of ``runtime/realtime-query.ts`` for ``invalidating_queries``' result."""
    entries = "\n".join(_entry(op, patterns) for op, patterns in queries.items())
    return (
        _HEADER % {"meta": META_KEY}
        + (_FILLED if any(_topic_expr(p)[1] for patterns in queries.values() for p in patterns) else "")
        + "\nconst TOPICS: Record<string, (props: Record<string, unknown>) => (string | null)[]> = {\n"
        + entries
        + "\n};\n\n"
        + f"export const {REALTIME_QUERY_EXPORT} = <T extends QueryOptionsWithMeta>(\n"
        + "  options: T,\n"
        + "  props: Record<string, unknown>,\n"
        + "  operation: OperationRef,\n"
        + "): T => {\n"
        + "  const topics = TOPICS[operation.operationId];\n"
        + "  if (!topics) return options;\n"
        + "  const names = topics(props).filter((name): name is string => name !== null);\n"
        + "  if (names.length === 0) return options;\n"
        + f"  return {{ ...options, meta: {{ ...options.meta, {META_KEY}: names }} }};\n"
        + "};\n"
    )


def query_option_overrides(queries: dict[str, list[str]], mutator_path: str) -> dict[str, dict[str, Any]]:
    """``override.operations`` entries pointing each tagged operation at the mutator."""
    return {
        op: {"query": {"queryOptions": {"path": mutator_path, "name": REALTIME_QUERY_EXPORT}}}
        for op in queries
    }


__all__ = [
    "META_KEY",
    "REALTIME_QUERY_EXPORT",
    "REALTIME_QUERY_FILE",
    "RealtimeInvalidationError",
    "invalidating_queries",
    "query_option_overrides",
    "render_realtime_query",
]
