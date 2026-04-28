"""OpenAPI string format → Zod expression."""

from __future__ import annotations

# Notes:
#   "date-time": offset:true accepts both Z and +HH:MM
#   "uri"/"url": FastAPI emits relative paths, z.string() is safe
#   "uuid": regex over z.uuid() — z.uuid() rejects some valid UUIDs (e.g. version 0)
ZOD_FORMAT_MAP: dict[str, str] = {
    "email": "z.email()",
    "date-time": "z.string().datetime({ offset: true })",
    "datetime": "z.string().datetime({ offset: true })",
    "date": "z.iso.date()",
    "uri": "z.string()",
    "url": "z.string()",
    "uuid": (
        "z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        "[0-9a-f]{4}-[0-9a-f]{12}$/i)"
    ),
}
