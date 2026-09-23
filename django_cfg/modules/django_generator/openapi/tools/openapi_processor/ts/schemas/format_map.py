"""OpenAPI string format → base Zod expression.

A format supplies the BASE expression only. `minLength`, `maxLength` and
`pattern` are applied on top of it by `converter._string()`, so a format never
costs a constraint — every value here must therefore accept `.min()`, `.max()`
and `.regex()` chained after it.
"""

from __future__ import annotations

# Notes:
#   "date-time": offset:true accepts both Z and +HH:MM
#   "uri"/"url": z.url() — DRF's URLField is always absolute, so a relative
#     path is a defect and not a case to tolerate. Previously z.string(), which
#     validated nothing.
#   "uuid": regex over z.uuid() — z.uuid() rejects some valid UUIDs (e.g. version 0)
ZOD_FORMAT_MAP: dict[str, str] = {
    "email": "z.email()",
    "date-time": "z.string().datetime({ offset: true })",
    "datetime": "z.string().datetime({ offset: true })",
    "date": "z.iso.date()",
    "uri": "z.url()",
    "url": "z.url()",
    "uuid": (
        "z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        "[0-9a-f]{4}-[0-9a-f]{12}$/i)"
    ),
}
