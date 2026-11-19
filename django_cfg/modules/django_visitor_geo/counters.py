"""Count visits by day and geography without storing anyone's address.

    bump_daily(PlaybackRegionDay, day=today, country=request.geo.country, lane="external")

One atomic statement per call (INSERT ... ON CONFLICT DO UPDATE), so concurrent requests never lose a count. The table
needs a unique constraint over exactly the dimension fields passed (here `day, country, lane`).
"""

from __future__ import annotations

from typing import Any

from django.db import connections, router


def bump_daily(model, *, field: str = "count", by: int = 1, **dims: Any) -> None:
    """Add `by` to `field` of the row identified by `dims`, creating it at `by`."""
    if not dims:
        raise ValueError("bump_daily needs the dimension fields (e.g. day=..., country=...)")
    meta = model._meta
    db = router.db_for_write(model)
    connection = connections[db]
    columns = [meta.get_field(name).column for name in dims]
    values = [meta.get_field(name).get_db_prep_save(value, connection) for name, value in dims.items()]
    counter = meta.get_field(field).column
    qn = connection.ops.quote_name
    if connection.vendor in ("postgresql", "sqlite"):
        sql = (
            f"INSERT INTO {qn(meta.db_table)} ({', '.join(qn(c) for c in columns)}, {qn(counter)}) "
            f"VALUES ({', '.join(['%s'] * len(values))}, %s) "
            f"ON CONFLICT ({', '.join(qn(c) for c in columns)}) "
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
