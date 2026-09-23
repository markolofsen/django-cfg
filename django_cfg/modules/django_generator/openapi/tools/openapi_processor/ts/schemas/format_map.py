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
#     validated nothing. A BLANK field is the exception, handled in
#     `converter._string()` rather than here: see EMPTY_STRING_FORMATS.
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


# Formats that reject "" but whose Django field routinely produces it.
#
# `URLField(blank=True)` and `EmailField(blank=True)` serialise an unset value
# as the empty string, not as null and not as an absent key — so a response
# carrying `"website": ""` is correct, ordinary data. `z.url()` rejects it, and
# the portal logged a zod validation error on every profile read of an account
# that had simply never filled the field in.
#
# drf-spectacular gives no direct signal for blank, but it does emit
# `minLength: 1` on a field that forbids it (a required write field), and that
# is the distinction `converter._string()` keys on: a format from this set with
# NO minLength accepts "" beside its own rule.
#
# The cost is a response field that is genuinely required-and-non-empty —
# `Lead.companyWebsite` — losing its emptiness check, because output schemas
# carry no minLength. That is the right trade: an unnoticed empty string beats
# a validation error raised against data the server is correct to send.
EMPTY_STRING_FORMATS: frozenset[str] = frozenset({"uri", "url", "email"})
