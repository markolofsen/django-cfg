"""The declared mapping of one Django model onto one Notion data source.

A mapping is data: which model field is the join key, which fields become which columns, which rows are left out and
why. There is no code per project beyond declaring it.

Guards that live here (each one is a real incident elsewhere):

* The join key is always written, from the same value the scan compares against. A row whose key was not stored
  attaches to nobody and is invisible to the next run's scan, so it would be created again.
* A field whose name says it is a secret (password, token, session, staff flag ...) cannot be mapped unless the
  mapping names it in ``allow_secret``. That is an explicit project override, never a default.
* Rich text is cut at 2000 UTF-16 units (``properties.utf16_pieces``), not characters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple
from urllib.parse import urlsplit

from ..details import is_forbidden
from ..exceptions import NotionError
from ..properties import rich_text

KINDS = ("title", "rich_text", "email", "phone_number", "url", "number", "checkbox", "date", "select")
KEY_KINDS = ("email", "rich_text", "title", "phone_number", "url")

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Substrings is_forbidden does not know, and whole words (short ones must not match inside other words).
_SECRET_PARTS = ("session", "credential", "permission", "passphrase", "private")
# A source that is a verb is an action, not a field: ``source="delete"`` would call ``obj.delete()`` for every row.
_ACTION_WORDS = {"delete", "save", "remove", "clear", "destroy", "drop", "reset", "truncate", "create", "update", "send", "refresh"}
_SECRET_WORDS = {"otp", "totp", "hash", "salt", "key", "staff", "superuser", "pwd", "auth", "jwt", "pin", "mfa"}


class ExportConfigError(NotionError):
    """A mapping that is wrong or would send something it must not. Raised when the mapping is built or checked."""


def secret_reason(name: str) -> Optional[str]:
    """Why ``name`` looks like a secret, or None."""
    if is_forbidden(name):
        return "its name says it is a secret"
    flat = re.sub(r"[^a-z0-9]", "", str(name).lower())
    if any(part in flat for part in _SECRET_PARTS):
        return "its name says it is a secret"
    words = set(re.split(r"[^a-z0-9]+", re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name)).lower()))
    if words & _SECRET_WORDS:
        return "its name says it is a secret or a permission"
    return None


@dataclass(frozen=True)
class ExportField:
    """One Notion column filled from one attribute of the model instance.

    ``source`` is an attribute name (a callable attribute, such as ``get_full_name``, is called without arguments;
    one marked ``alters_data`` or named like an action, such as ``delete``, is refused).
    ``transform(value, obj)`` may reshape it. An empty value leaves the column out; a ``checkbox`` always has a value.
    """

    column: str
    source: str
    kind: str = "rich_text"
    transform: Optional[Callable[[Any, Any], Any]] = None


@dataclass(frozen=True)
class Exclusion:
    """A reason to leave a row out. ``when(obj, now)`` is true to exclude. The first matching reason is counted."""

    reason: str
    when: Callable[[Any, datetime], bool]


@dataclass(frozen=True)
class ExportMapping:
    """``key`` is the join key: its column is where the scan looks for rows that are already in Notion."""

    model: str                                  # "app_label.ModelName"
    key: ExportField
    fields: Tuple[ExportField, ...] = ()
    exclusions: Tuple[Exclusion, ...] = ()
    queryset: Optional[Callable[[Any], Any]] = None
    batch_column: Optional[str] = "Import batch"
    # The row's project key (``keys.for_object``: the user's site -> NotionConfig.project_keys) as the matching live
    # option of this multi_select column. Written on create; on a row already in Notion it is added, never removed.
    projects_column: Optional[str] = None
    allow_secret: FrozenSet[str] = frozenset()  # explicit override: attribute names that may be mapped though they look secret

    def __post_init__(self) -> None:
        if "." not in self.model:
            raise ExportConfigError(f"model must be 'app_label.ModelName', got {self.model!r}")
        if self.key.kind not in KEY_KINDS:
            raise ExportConfigError(f"the join key kind must be one of {KEY_KINDS}, got {self.key.kind!r}")
        columns = [f.column for f in (self.key, *self.fields)]
        columns += [c for c in (self.batch_column, self.projects_column) if c]
        if len(set(columns)) != len(columns):
            raise ExportConfigError("two fields (or a field and the batch or projects column) write the same Notion column")
        for f in (self.key, *self.fields):
            if re.split(r"[^a-z0-9]+", f.source.lower())[0] in _ACTION_WORDS:
                raise ExportConfigError(f"column {f.column!r} reads {f.source!r}, which is an action, not a field: it would run on every row")
            if f.kind not in KINDS:
                raise ExportConfigError(f"column {f.column!r}: unknown kind {f.kind!r}")
            reason = secret_reason(f.source)
            if reason and f.source not in self.allow_secret:
                raise ExportConfigError(
                    f"column {f.column!r} reads {f.source!r}, which is refused: {reason}. "
                    f"Name it in allow_secret only if you really mean to send it to Notion."
                )

    @property
    def columns(self) -> Tuple[str, ...]:
        cols = [self.key.column, *(f.column for f in self.fields)]
        cols += [c for c in (self.batch_column, self.projects_column) if c]
        return tuple(cols)

    def column_kinds(self) -> Dict[str, str]:
        kinds = {f.column: f.kind for f in (self.key, *self.fields)}
        if self.batch_column:
            kinds[self.batch_column] = "rich_text"
        if self.projects_column:
            kinds[self.projects_column] = "multi_select"
        return kinds


def read(obj: Any, f: ExportField) -> Any:
    value = getattr(obj, f.source, None)
    if callable(value):
        if getattr(value, "alters_data", False):  # Django's own marker (save, delete, ...): never called from an export
            raise ExportConfigError(f"{f.source!r} alters data; an export only reads")
        value = value()
    return f.transform(value, obj) if f.transform else value


def normalize_key(kind: str, value: Any) -> str:
    text = ("" if value is None else str(value)).strip()
    return text.lower() if kind == "email" else text


def key_of(mapping: ExportMapping, obj: Any) -> str:
    """The normalized join key, or "" when the row has none that Notion would accept."""
    key = normalize_key(mapping.key.kind, read(obj, mapping.key))
    if mapping.key.kind == "email" and not _EMAIL.match(key):
        return ""
    return key


def _iso(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def to_property(kind: str, value: Any) -> Optional[Dict[str, Any]]:
    """The Notion property value for ``value``, or None when it is empty or this column cannot hold it."""
    if kind == "checkbox":
        return {"checkbox": bool(value)}
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if kind == "title":
        return {"title": rich_text(str(value))}
    if kind == "rich_text":
        return {"rich_text": rich_text(str(value))}
    text = str(value).strip()
    if kind == "email":
        return {"email": text} if _EMAIL.match(text) else None
    if kind == "phone_number":
        return {"phone_number": text[:200]} if re.search(r"\d{5,}", text) else None
    if kind == "url":
        parts = urlsplit(text)
        return {"url": text} if parts.scheme in ("http", "https") and parts.netloc and len(text) <= 2000 else None
    if kind == "number":
        try:
            return {"number": float(value)}
        except (TypeError, ValueError):
            return None
    if kind == "date":
        return {"date": {"start": _iso(value)}}
    if kind == "select":
        return {"select": {"name": text.replace(",", " ")[:100]}}
    return None


def build_properties(mapping: ExportMapping, obj: Any, key: str, batch: str, project_option: Optional[str] = None) -> Dict[str, Any]:
    """The ``properties`` of ``pages.create``. The key column is always present and always holds ``key``.

    ``project_option`` is the live option of ``projects_column`` for the row's project key (None: not written).
    """
    props: Dict[str, Any] = {}
    value = to_property(mapping.key.kind, key)
    if value is None:
        raise ExportConfigError("the join key cannot be written to its column")
    props[mapping.key.column] = value
    for f in mapping.fields:
        value = to_property(f.kind, read(obj, f))
        if value is not None:
            props[f.column] = value
    if mapping.batch_column and batch:
        props[mapping.batch_column] = {"rich_text": rich_text(batch)}
    if mapping.projects_column and project_option:
        props[mapping.projects_column] = {"multi_select": [{"name": project_option}]}
    return props


def multi_select_names(prop: Dict[str, Any]) -> List[str]:
    """The option names of a multi_select property as Notion returns it."""
    return [o.get("name", "") for o in (prop or {}).get("multi_select") or [] if o.get("name")]


def plain(prop: Dict[str, Any]) -> str:
    """The text of a property as Notion returns it (a query result or a created page)."""
    kind = prop.get("type") or next((k for k in ("title", "rich_text", "email", "phone_number", "url") if k in prop), None)
    if kind in ("rich_text", "title"):
        return "".join(t.get("plain_text") or (t.get("text") or {}).get("content", "") for t in prop.get(kind) or [])
    if kind in ("email", "phone_number", "url"):
        return prop.get(kind) or ""
    return ""
