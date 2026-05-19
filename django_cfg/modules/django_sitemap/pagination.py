"""Keyset pagination over a Django queryset.

The contract:

    rows, next_cursor = keyset_page(qs, source, cursor=None)

`source.cursor_fields` is the tuple of fields used for both ordering and
keyset filtering. `source.order` is parsed once for the SQL `ORDER BY`.
A cursor (decoded into a tuple of values matching `cursor_fields`) means
"give me rows strictly after these values in the declared order".

We fetch `page_size + 1` rows to detect whether a next page exists
without doing a second COUNT.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django.db.models import Q, QuerySet

from .sources import SitemapSource, resolve_field


def keyset_page(
    qs: QuerySet,
    source: SitemapSource,
    cursor: tuple[Any, ...] | None,
) -> tuple[list[Any], tuple[Any, ...] | None]:
    """Return one page of rows + the cursor for the next page (or None)."""
    order_directions = _parse_order(source.order, source.cursor_fields)

    if cursor is not None:
        if len(cursor) != len(source.cursor_fields):
            raise ValueError(
                f"cursor arity mismatch: expected {len(source.cursor_fields)}, "
                f"got {len(cursor)}"
            )
        cursor_values = tuple(
            _coerce(v, source.cursor_fields[i], qs)
            for i, v in enumerate(cursor)
        )
        qs = qs.filter(_keyset_filter(source.cursor_fields, order_directions, cursor_values))

    order_args = [
        f"-{f}" if order_directions[f] == "desc" else f
        for f in source.cursor_fields
    ]
    rows = list(qs.order_by(*order_args)[: source.page_size + 1])

    if len(rows) <= source.page_size:
        return rows, None

    page = rows[: source.page_size]
    last = page[-1]
    next_cursor = tuple(resolve_field(last, _orm_path(f)) for f in source.cursor_fields)
    return page, next_cursor


def _parse_order(order: str, cursor_fields: tuple[str, ...]) -> dict[str, str]:
    """`"-last_seen_at,-id"` → {"last_seen_at": "desc", "id": "desc"}."""
    out: dict[str, str] = {}
    for chunk in order.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("-"):
            out[chunk[1:]] = "desc"
        else:
            out[chunk] = "asc"
    missing = [f for f in cursor_fields if f not in out]
    if missing:
        raise ValueError(
            f"source.order is missing cursor field(s) {missing}: {order!r}"
        )
    return out


def _keyset_filter(
    cursor_fields: tuple[str, ...],
    directions: dict[str, str],
    values: tuple[Any, ...],
) -> Q:
    """Tuple-comparison filter for keyset pagination.

    Conceptually: `(f1, f2, ..., fn) <order> (v1, v2, ..., vn)`.

    Django ORM doesn't speak tuple comparison directly, so we expand it:
    `(f1 < v1) OR (f1 == v1 AND f2 < v2) OR ... `
    """
    or_terms: list[Q] = []
    for i, field in enumerate(cursor_fields):
        eq_kwargs = {cursor_fields[j]: values[j] for j in range(i)}
        cmp_lookup = "lt" if directions[field] == "desc" else "gt"
        eq_kwargs[f"{field}__{cmp_lookup}"] = values[i]
        or_terms.append(Q(**eq_kwargs))
    combined: Q = or_terms[0]
    for term in or_terms[1:]:
        combined = Q(combined | term)
    return combined


def _orm_path(field: str) -> str:
    """Convert ORM-style `brand__slug` to attr path `brand.slug`."""
    return field.replace("__", ".")


def _coerce(value: Any, field: str, qs: QuerySet) -> Any:
    """Coerce a JSON-decoded cursor value back into a Python value.

    The only non-trivial case: datetimes arrive as ISO strings. We probe
    the model field type once and convert.
    """
    if not isinstance(value, str):
        return value
    model = qs.model
    if model is None:
        return value
    try:
        model_field = model._meta.get_field(field.split("__")[0])
    except Exception:
        return value
    internal = model_field.get_internal_type()
    if internal in ("DateTimeField",):
        return datetime.fromisoformat(value)
    if internal in ("DateField",):
        return date.fromisoformat(value)
    return value
