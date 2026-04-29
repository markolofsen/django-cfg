"""Per-file fixers for openapi-python-client generated output.

Each fixer is a pure function: takes file text, returns (new_text, changed).
Fixers are intentionally minimal — they only touch generated files and
only fix known upstream bugs. They MUST be idempotent.
"""

from __future__ import annotations

import re

# Matches the import line that openapi-python-client emits when a file
# uses both UNSET (the sentinel) and Response (the wrapper) but forgot
# to also import the Unset *type*. We rewrite it to include Unset.
#
# Concrete example from the wild:
#   from ...types import UNSET, Response
# becomes:
#   from ...types import UNSET, Unset, Response
#
# Idempotent: if Unset is already in the import, the regex won't match.
_TYPES_IMPORT_RE = re.compile(
    r"^(?P<prefix>from\s+(?:\.+)types\s+import\s+)UNSET,\s*Response(?P<suffix>\s*)$",
    re.MULTILINE,
)

# Sentinel that proves the file actually uses the Unset *type* in a
# signature. We only inject the import when this pattern is present —
# otherwise the import would be unused and ruff/pyright would flag it.
_UNSET_TYPE_USAGE_RE = re.compile(r"\|\s*Unset\b")


def fix_unset_import(text: str) -> tuple[str, bool]:
    """Inject ``Unset`` into the ``...types`` import when needed.

    Returns (new_text, changed). Only changes files that:
      1. Import ``UNSET, Response`` from ``...types`` (no ``Unset``).
      2. Reference the ``Unset`` type elsewhere (e.g. ``| Unset = UNSET``).
    """
    if not _UNSET_TYPE_USAGE_RE.search(text):
        return text, False
    new_text, n = _TYPES_IMPORT_RE.subn(
        r"\g<prefix>UNSET, Unset, Response\g<suffix>",
        text,
        count=1,
    )
    return new_text, n > 0


# Pattern for the second known upstream bug: enum-typed nullable fields.
#
# openapi-python-client emits this for ``foo: SomeEnum | None | Unset``:
#
#     foo: <T> | Unset = UNSET
#     if not isinstance(self.foo, Unset):
#         foo = self.foo.value
#
# The check ``not isinstance(..., Unset)`` does not exclude ``None`` — so
# when the runtime value is ``None`` (typed as ``T | None | Unset``), the
# ``.value`` access crashes with ``AttributeError: 'NoneType' object has
# no attribute 'value'``. We rewrite the guard to also exclude ``None``.
#
# Match groups:
#   indent   — leading whitespace of the ``if`` line
#   field    — the attribute name (e.g. ``self.photo_type``)
# We require the ``.value`` access on the next line to belong to the same
# ``self.<field>`` so we don't accidentally rewrite unrelated branches.
_ENUM_VALUE_GUARD_RE = re.compile(
    r"^(?P<indent>[ \t]*)if not isinstance\((?P<field>self\.\w+), Unset\):\n"
    r"(?P=indent)[ \t]+\w+ = (?P=field)\.value$",
    re.MULTILINE,
)


def fix_enum_value_none_guard(text: str) -> tuple[str, bool]:
    """Add ``is not None`` to enum-``.value`` guards.

    Rewrites::

        if not isinstance(self.x, Unset):
            x = self.x.value

    into::

        if self.x is not None and not isinstance(self.x, Unset):
            x = self.x.value

    Idempotent: once the ``is not None`` guard is in place, the regex
    won't match again on the next pass.
    """
    def _replace(m: re.Match[str]) -> str:
        indent = m.group("indent")
        field = m.group("field")
        body_line = m.group(0).split("\n", 1)[1]
        return (
            f"{indent}if {field} is not None and not isinstance({field}, Unset):\n"
            f"{body_line}"
        )

    new_text, n = _ENUM_VALUE_GUARD_RE.subn(_replace, text)
    return new_text, n > 0


__all__ = ["fix_enum_value_none_guard", "fix_unset_import"]
