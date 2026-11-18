"""Plan, scan, execute and report for one export. One way only: Django to Notion.

Three layers, so the interesting one needs no network:

* ``build_plan``  reads the ORM (SELECT only) and decides which rows are exported and which are left out, and why.
* ``scan``        reads the key column of the Notion data source, so a row that is already there is never created twice.
* ``execute``     talks to Notion through a client object (``data_sources.query/retrieve``, ``pages.create``).

Nothing is ever updated or deleted: the integration cannot delete, and an edit made in Notion is never read back into
Django. A report and a manifest carry counts, primary keys and page ids, never a name, an email or a phone.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from django.utils import timezone

from .mapping import (
    ExportConfigError,
    ExportMapping,
    build_properties,
    key_of,
    normalize_key,
    plain,
)
from .throttle import Throttle

logger = logging.getLogger(__name__)


def mask(value: str) -> str:
    """A shape that tells nothing: first character and the fact it was an address."""
    value = value or ""
    return f"{value[:1]}***@***" if "@" in value else f"{value[:1]}***"


# ─── plan ────────────────────────────────────────────────────────────────────


@dataclass
class Record:
    pk: Any
    key: str
    obj: Any = field(repr=False)


@dataclass
class Plan:
    mapping: ExportMapping
    records: List[Record] = field(default_factory=list)
    scanned: int = 0
    excluded: Counter = field(default_factory=Counter)


_warned = set()


def _warn_once(what: str, exc: Exception) -> None:
    """One log line per kind of failure, with the exception type only (the text can carry a value of the row)."""
    if what not in _warned:
        _warned.add(what)
        logger.warning("notion_export: %s failed on a row (%s); such rows are left out and counted", what, type(exc).__name__)


def _exclusion(mapping: ExportMapping, obj: Any, now: datetime) -> Optional[str]:
    """The reason to leave ``obj`` out. A rule that raises leaves the row out (never exports it) and does not stop the plan."""
    for e in mapping.exclusions:
        try:
            if e.when(obj, now):
                return e.reason
        except ExportConfigError:
            raise
        except Exception as exc:
            _warn_once("exclusion", exc)
            return f"{e.reason} (rule failed, row left out)"
    return None


def build_plan(mapping: ExportMapping, model, *, now: Optional[datetime] = None) -> Plan:
    now = now or timezone.now()
    qs = model._default_manager.all()
    if mapping.queryset is not None:
        qs = mapping.queryset(qs)
    plan = Plan(mapping)
    seen = set()
    for obj in qs.order_by("pk").iterator(chunk_size=1000):
        plan.scanned += 1
        reason = _exclusion(mapping, obj, now)
        if reason:
            plan.excluded[reason] += 1
            continue
        try:
            key = key_of(mapping, obj)
        except ExportConfigError:
            raise
        except Exception as exc:
            _warn_once("key", exc)
            plan.excluded["key could not be read (row left out)"] += 1
            continue
        if not key:
            plan.excluded["no valid key"] += 1
            continue
        if key in seen:
            plan.excluded["duplicate key (first row wins)"] += 1
            continue
        seen.add(key)
        plan.records.append(Record(obj.pk, key, obj))
    return plan


# ─── notion io ───────────────────────────────────────────────────────────────


def scan(client, throttle: Throttle, data_source: str, mapping: ExportMapping) -> Dict[str, str]:
    """Normalized key -> page id for every row of the data source, one paginated read. Read only."""
    column, kind = mapping.key.column, mapping.key.kind
    rows: Dict[str, str] = {}
    cursor = None
    while True:
        kwargs: Dict[str, Any] = {"page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        res = throttle.call(client.data_sources.query, data_source, **kwargs)
        for page in res.get("results", []):
            text = normalize_key(kind, plain(page.get("properties", {}).get(column, {})))
            if text:
                rows.setdefault(text, page["id"])
        if not res.get("has_more"):
            return rows
        cursor = res.get("next_cursor")


def schema_problems(client, throttle: Throttle, data_source: str, mapping: ExportMapping) -> List[str]:
    schema = throttle.call(client.data_sources.retrieve, data_source).get("properties", {})
    out: List[str] = []
    for column, kind in mapping.column_kinds().items():
        if column not in schema:
            out.append(f"missing column '{column}'")
            continue
        actual = (schema[column] or {}).get("type")
        if actual and actual != kind:
            out.append(f"column '{column}' is {actual}, the mapping writes {kind}")
    return out


# ─── execute ─────────────────────────────────────────────────────────────────


@dataclass
class Report:
    scanned: int = 0
    excluded: Counter = field(default_factory=Counter)
    planned: int = 0
    existing: int = 0
    new: int = 0
    created: int = 0
    unverified: int = 0                                 # created, but the response did not echo the key column
    errors: Counter = field(default_factory=Counter)    # error code -> count; never the provider's text
    blockers: List[str] = field(default_factory=list)
    manifest: List[Tuple[Any, str]] = field(default_factory=list)   # (primary key, page id): no PII

    def lines(self, *, apply: bool, limit: Optional[int] = None) -> List[str]:
        out = [f"database: {self.scanned} rows read"]
        out += [f"  excluded {n:>6}  {reason}" for reason, n in sorted(self.excluded.items())]
        out.append(f"planned: {self.planned}; already in Notion: {self.existing}; new: {self.new}")
        if not apply:
            out.append(f"would create: {self.new if limit is None else min(self.new, limit)}")
        else:
            out.append(f"created: {self.created} (key not echoed back for {self.unverified}); errors {dict(self.errors)}")
        out += [f"BLOCKER: {b}" for b in self.blockers]
        return out


def _code(exc: Exception) -> str:
    return str(getattr(exc, "code", None) or type(exc).__name__)[:60]


def execute(
    plan: Plan, client, data_source: str, *, apply: bool, batch: str, limit: Optional[int] = None,
    throttle: Optional[Throttle] = None, read_notion: bool = True, manifest_path: Optional[str] = None,
) -> Report:
    """Dry run (``apply=False``) reads Notion and counts; it never calls ``pages.create``.

    ``manifest_path``: every created page is appended there (``pk<TAB>page id<TAB>batch``) the moment it exists, so an
    interrupted run still leaves the list of what it wrote.
    """
    th = throttle or Throttle()
    mapping = plan.mapping
    rep = Report(scanned=plan.scanned, excluded=Counter(plan.excluded), planned=len(plan.records))
    existing: Dict[str, str] = {}

    if read_notion and client is not None:
        try:
            existing = scan(client, th, data_source, mapping)
            rep.blockers += [f"data source: {p}" for p in schema_problems(client, th, data_source, mapping)]
        except Exception as exc:
            rep.blockers.append(f"data source not readable ({_code(exc)})")
    elif apply:
        rep.blockers.append("apply needs to read Notion first, or a re-run would create everything again")

    todo = [r for r in plan.records if r.key not in existing]
    rep.existing = len(plan.records) - len(todo)
    rep.new = len(todo)
    if not apply:
        return rep
    if rep.blockers or client is None:
        rep.blockers.append("apply refused: fix the blockers above first")
        return rep

    manifest = None
    if manifest_path:
        try:
            manifest = open(manifest_path, "a", encoding="utf-8")
        except OSError as exc:
            rep.blockers.append(f"manifest not writable ({type(exc).__name__}); nothing was created")
            return rep
    try:
        _create_all(rep, todo, mapping, th, client, data_source, batch, limit, manifest)
    finally:
        if manifest is not None:
            manifest.close()
    return rep


def _create_all(rep, todo, mapping, th, client, data_source, batch, limit, manifest) -> None:
    for rec in todo:
        if limit is not None and rep.created >= limit:
            break
        try:
            page = th.call(client.pages.create, parent={"data_source_id": data_source},
                           properties=build_properties(mapping, rec.obj, rec.key, batch))
        except ExportConfigError as exc:  # the mapping is wrong for every row: stop, do not try each one
            rep.blockers.append(f"mapping refused: {exc}")
            break
        except Exception as exc:
            rep.errors[_code(exc)] += 1
            continue
        rep.created += 1
        rep.manifest.append((rec.pk, page["id"]))
        if manifest is not None:
            manifest.write(f"{rec.pk}\t{page['id']}\t{batch}\n")
            manifest.flush()
        props = page.get("properties")
        if props is None:
            rep.unverified += 1
        elif normalize_key(mapping.key.kind, plain(props.get(mapping.key.column, {}))) != rec.key:
            # Every further row would be written without its join key too, and the next run would create it again.
            rep.errors["key_not_stored"] += 1
            rep.blockers.append("a page was created without its key in the key column; stopped (check the column type)")
            break
