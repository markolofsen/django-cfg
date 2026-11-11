"""Stamp a generated target with the django-cfg that produced it.

Runs AFTER the tool and the output cache, on every outcome (fresh or replayed), so the stamp never enters a cache key and a
cache hit never keeps an old one. Writes only two things:

* `info["x-cfg-version"]` / `info["x-cfg-contract"]` in every `openapi.json` of the target (all languages have one);
* `helpers/cfg.ts` for a TypeScript target: `CFG = { version, contract }`, readable at runtime by a client that wants to compare.

`version` is the django-cfg that generated the client; `contract` is the oldest django-cfg that serves the same contract
(`django_cfg.core.contract.CONTRACT_SINCE`), i.e. the minimum a host must run.
"""

from __future__ import annotations

import json
from pathlib import Path

from ...tools.openapi_processor.ts.wrapper.templates.cfg import render_cfg_ts
from django_cfg.core.contract import CFG_VERSION, CONTRACT_SINCE, SPEC_KEY_CONTRACT, SPEC_KEY_VERSION

def stamp_target(out_root: Path) -> None:
    """Idempotent: a second run over the same target writes the same bytes."""
    out_root = Path(out_root)
    for spec in _specs(out_root):
        _stamp_spec(spec)
    helpers = out_root / "helpers"
    if helpers.is_dir():
        text = render_cfg_ts()
        path = helpers / "cfg.ts"
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")


def _specs(root: Path) -> list[Path]:
    found = [root / "openapi.json"]
    found += sorted(root.glob("*/openapi.json"))
    return [p for p in found if p.is_file()]


def _stamp_spec(path: Path) -> None:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    info = spec.get("info")
    if not isinstance(info, dict):
        return
    if info.get(SPEC_KEY_VERSION) == CFG_VERSION and info.get(SPEC_KEY_CONTRACT) == CONTRACT_SINCE:
        return
    info[SPEC_KEY_VERSION] = CFG_VERSION
    info[SPEC_KEY_CONTRACT] = CONTRACT_SINCE
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def check_stamps(paths: list[Path]) -> list[str]:
    """What is wrong with the stamped targets at `paths`, one line each; empty = every client matches this django-cfg.

    The rule is equality of `contract`, not of `version`: a patch release changes no contract and asks for no regeneration.
    A client with a different contract was made for a django-cfg this host does not run (older or newer): regenerate or update.
    """
    problems: list[str] = []
    for root in paths:
        root = Path(root)
        specs = _specs(root)
        if not specs:
            problems.append(f"{root}: no openapi.json (not generated yet?)")
            continue
        for spec in specs:
            try:
                info = json.loads(spec.read_text(encoding="utf-8")).get("info") or {}
            except (OSError, ValueError):
                problems.append(f"{spec}: unreadable")
                continue
            contract = info.get(SPEC_KEY_CONTRACT)
            if contract is None:
                problems.append(f"{spec}: not stamped (generated before the CFG stamp); regenerate with `manage.py gen`")
            elif contract != CONTRACT_SINCE:
                problems.append(
                    f"{spec}: contract {contract} (made by django-cfg {info.get(SPEC_KEY_VERSION, '?')}), "
                    f"this host's contract is {CONTRACT_SINCE} (django-cfg {CFG_VERSION}); regenerate or align django-cfg"
                )
    return problems
