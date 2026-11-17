"""Read-only checks of the Notion setup. Creates and changes nothing in Notion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from . import client as client_mod
from . import conf
from .__cfg__ import COLUMN_TYPES, DEFAULT_COLUMNS, NotionTarget
from .exceptions import NotionConfigError

OK, WARN, ERROR = "ok", "warn", "error"


@dataclass
class Finding:
    level: str
    where: str
    message: str


def _no_read(exc: Exception) -> bool:
    return getattr(exc, "status", None) in (403, 404) or getattr(exc, "code", "") in ("restricted_resource", "object_not_found")


def check_target(client, name: str, target: NotionTarget) -> List[Finding]:
    out: List[Finding] = []
    try:
        ds_id = client_mod.resolve_data_source(client, target)
    except NotionConfigError as exc:
        return [Finding(ERROR, name, str(exc))]
    except Exception as exc:
        if _no_read(exc):
            return [Finding(WARN, name, "cannot read the database (the token may be Insert-only or the database is not shared "
                            "with the integration); set data_source_id and test with a staging lead")]
        return [Finding(ERROR, name, f"database lookup failed: {type(exc).__name__}: {getattr(exc, 'message', exc)}")]
    try:
        ds: Any = client.data_sources.retrieve(ds_id)
    except Exception as exc:
        if _no_read(exc):
            return [Finding(WARN, name, "cannot read the data source schema (Insert-only token?): columns not verified")]
        return [Finding(ERROR, name, f"data source lookup failed: {type(exc).__name__}: {getattr(exc, 'message', exc)}")]
    props = ds.get("properties") or {}
    for logical in DEFAULT_COLUMNS:
        column = target.column(logical)
        if column is None:
            continue
        spec = props.get(column)
        if spec is None:
            out.append(Finding(ERROR, name, f"missing column {column!r} ({COLUMN_TYPES[logical]})"))
        elif spec.get("type") != COLUMN_TYPES[logical]:
            out.append(Finding(ERROR, name, f"column {column!r} is {spec.get('type')}, need {COLUMN_TYPES[logical]}"))
    for logical, wanted in (("status", ["New"]), ("source", ["Website"])):
        column = target.column(logical)
        spec = props.get(column or "")
        if spec and spec.get("type") == "select":
            names = {o.get("name") for o in spec["select"].get("options", [])}
            for w in wanted:
                if w not in names:
                    out.append(Finding(WARN, name, f"{column!r} has no option {w!r} (Notion would create it)"))
    if not out:
        out.append(Finding(OK, name, f"data source {ds_id}: all columns present with the right types"))
    return out


def run() -> List[Finding]:
    try:
        cfg = conf.get_notion_config()
    except NotionConfigError as exc:
        return [Finding(ERROR, "config", str(exc))]
    findings: List[Finding] = []
    if not cfg.targets:
        return [Finding(ERROR, "config", "no targets configured")]
    for name, target in cfg.targets.items():
        try:
            client = client_mod.get_client(target)
        except NotionConfigError as exc:
            findings.append(Finding(ERROR, name, str(exc)))
            continue
        try:
            client.users.me()
            findings.append(Finding(OK, name, "token accepted by Notion"))
        except Exception as exc:
            findings.append(Finding(ERROR, name, f"Notion rejected the token: {type(exc).__name__}: {getattr(exc, 'message', '')}"))
            continue
        findings.extend(check_target(client, name, target))
    return findings
