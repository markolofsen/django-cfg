"""Count visits by day and geography without storing anyone's address.

    bump_daily(PlaybackRegionDay, field="started", day=today, country=request.geo.country, lane="external")

One atomic statement per call (INSERT ... ON CONFLICT DO UPDATE), so concurrent requests never lose a count. The table
needs a unique constraint over exactly the dimension fields passed (here `day, country, lane`).

The first insert of a row fills every other column the way `Model.objects.create()` would: its `default` (a sibling
counter with `default=0` starts at 0), `auto_now`/`auto_now_add` with the current time, NULL when nullable. A NOT NULL
column with no default cannot be filled and raises `ValueError` before any SQL runs: a misconfigured counter fails
loudly in the caller's tests, not silently in production.
"""

from __future__ import annotations

from typing import Any, Dict

from django.db import connections, router
from django.db.models.fields import AutoFieldMixin
from django.utils import timezone


def _other_columns(model, skip) -> Dict[str, Any]:
    """Values for the columns the caller did not name, as `create()` would give them."""
    values: Dict[str, Any] = {}
    for field in model._meta.concrete_fields:
        if field.name in skip or isinstance(field, AutoFieldMixin):
            continue
        if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            values[field.name] = timezone.now()
        elif field.has_default():
            values[field.name] = field.get_default()
        elif field.has_db_default():
            continue  # the database fills it
        elif field.null:
            continue
        else:
            raise ValueError(
                f"bump_daily({model.__name__}): column {field.name!r} is NOT NULL and has no default; "
                f"give it default=... (a sibling counter: default=0) or pass it as a dimension"
            )
    return values


def bump_daily(model, *, field: str = "count", by: int = 1, **dims: Any) -> None:
    """Add `by` to `field` of the row identified by `dims`, creating it at `by`."""
    if not dims:
        raise ValueError("bump_daily needs the dimension fields (e.g. day=..., country=...)")
    meta = model._meta
    others = _other_columns(model, set(dims) | {field})
    db = router.db_for_write(model)
    connection = connections[db]
    if connection.vendor in ("postgresql", "sqlite"):
        insert = {**dims, **others}
        names = list(insert)
        columns = [meta.get_field(name).column for name in names]
        values = [meta.get_field(name).get_db_prep_save(insert[name], connection) for name in names]
        keys = [meta.get_field(name).column for name in dims]
        counter = meta.get_field(field).column
        qn = connection.ops.quote_name
        sql = (
            f"INSERT INTO {qn(meta.db_table)} ({', '.join(qn(c) for c in columns)}, {qn(counter)}) "
            f"VALUES ({', '.join(['%s'] * len(values))}, %s) "
            f"ON CONFLICT ({', '.join(qn(c) for c in keys)}) "
            f"DO UPDATE SET {qn(counter)} = {qn(meta.db_table)}.{qn(counter)} + EXCLUDED.{qn(counter)}"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, [*values, by])
        return
    # Other backends: ORM upsert, correct but not race-free on first insert.
    from django.db.models import F

    updated = model.objects.using(db).filter(**dims).update(**{field: F(field) + by})
    if not updated:
        model.objects.using(db).create(**dims, **{field: by})
