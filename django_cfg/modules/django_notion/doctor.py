"""Read-only checks of the Notion setup. Creates and changes nothing in Notion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import client as client_mod
from . import conf, keys
from .__cfg__ import COLUMN_TYPES, DEFAULT_COLUMNS, NotionTarget
from .exceptions import NotionConfigError

OK, WARN, ERROR = "ok", "warn", "error"


@dataclass
class Finding:
    level: str
    where: str
    message: str
    project_key: str = ""  # set on a Brand-option match, so run() can tell which keys matched nowhere


def _no_read(exc: Exception) -> bool:
    return getattr(exc, "status", None) in (403, 404) or getattr(exc, "code", "") in ("restricted_resource", "object_not_found")


def check_target(client, name: str, target: NotionTarget, project_keys: Optional[Dict[str, str]] = None) -> List[Finding]:
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
            out = [Finding(WARN, name, "cannot read the data source schema (Insert-only token?): columns not verified")]
            if project_keys:
                out.append(Finding(WARN, name, "the Brand option is matched from the live schema: with no Read content every "
                                   "lead goes with Brand empty; give the integration Read content"))
            return out
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
    out += _brand_options(name, target, props, project_keys or {})
    return out


def _brand_options(name: str, target: NotionTarget, props: dict, project_keys: Dict[str, str]) -> List[Finding]:
    """The project keys this target's live Brand options match (OK), and keys matching two options (WARN).

    A key with no option here is not reported per target: it may route to another one. ``run`` warns about a key that
    matches no target at all.
    """
    column = target.column("brand")
    spec = props.get(column or "") or {}
    if not project_keys or spec.get("type") != "multi_select":
        return []
    names = [o.get("name", "") for o in (spec.get("multi_select") or {}).get("options", [])]
    out: List[Finding] = []
    for key in sorted(set(project_keys.values())):
        hits = [n for n in names if keys.normalize(n) == keys.normalize(key)]
        if len(hits) == 1:
            out.append(Finding(OK, name, f"project key {key!r} -> {column!r} option {hits[0]!r}", project_key=key))
        elif len(hits) > 1:
            out.append(Finding(WARN, name, f"project key {key!r} matches {len(hits)} {column!r} options {hits}; Brand left empty"))
    return out


def check_keys(cfg) -> List[Finding]:
    """``project_keys`` against the registered sites: a key for an unknown site never fires, a site without one writes no key."""
    try:
        from django_cfg.core.site import sites

        registered = [s.key for s in sites()]
    except Exception:
        registered = []
    if not cfg.project_keys:
        return [Finding(WARN, "project_keys", "no project keys: leads carry no project key and no Brand "
                        "(set NotionConfig.project_keys, e.g. {'default': 'carapis'})")]
    out: List[Finding] = []
    for site in sorted(set(cfg.project_keys) - set(registered)):
        out.append(Finding(ERROR, "project_keys", f"site {site!r} is not a registered site {registered}: its key is never used"))
    for site in registered:
        if site not in cfg.project_keys:
            out.append(Finding(WARN, "project_keys", f"site {site!r} has no project key: its leads carry none"))
    if not out:
        out.append(Finding(OK, "project_keys", ", ".join(f"{s} -> {k}" for s, k in sorted(cfg.project_keys.items()))))
    return out


def run() -> List[Finding]:
    try:
        cfg = conf.get_notion_config()
    except NotionConfigError as exc:
        return [Finding(ERROR, "config", str(exc))]
    findings: List[Finding] = check_keys(cfg)
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
        findings.extend(check_target(client, name, target, cfg.project_keys))
    matched = {f.project_key for f in findings if f.project_key}
    for key in sorted(set(cfg.project_keys.values()) - matched):
        findings.append(Finding(WARN, "project_keys", f"project key {key!r} matches no Brand option on any readable target: "
                                "its leads go with Brand empty (add the option, e.g. with the Hub's notion.projects step)"))
    return findings
