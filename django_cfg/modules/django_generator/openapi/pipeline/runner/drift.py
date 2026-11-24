"""Has the Django schema moved since a target was generated? Answered without running a tool.

Every target keeps the slice it was generated from as ``openapi.json`` next to its output (one per group folder for a
split target). ``check_drift`` renders the spec, cuts each target's slice exactly as ``dispatch.prepare_slice`` does, and
compares it with that file, stamp keys aside (the stamp check owns them). A difference means the committed client no
longer matches the API: run ``make gen``.

Not covered, on purpose: a hand edit of generated files (``make gen`` + ``git diff --exit-code`` catches that) and a
generator change with the same contract (a patch release asks for no regeneration; see ``stamp.check_stamps``).
Proto targets are skipped: their output follows the ``.proto`` files, not the OpenAPI slice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django_cfg.core.contract import SPEC_KEY_CONTRACT, SPEC_KEY_VERSION

from ..config import GenerationTarget, OpenAPIConfig, RunReport
from ..errors import GeneratorError
from .dispatch import output_units, prepare_slice
from .paths import cache_dir

_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def _comparable(spec: dict[str, Any]) -> dict[str, Any]:
    spec = dict(spec)
    if isinstance(spec.get("info"), dict):
        spec["info"] = {k: v for k, v in spec["info"].items() if k not in (SPEC_KEY_VERSION, SPEC_KEY_CONTRACT)}
    # Round-trip through JSON: the committed file went through it (tuples, key order of nested dicts).
    return json.loads(json.dumps(spec, ensure_ascii=False))


def _operations(spec: dict[str, Any]) -> dict[str, Any]:
    ops: dict[str, Any] = {}
    for path, item in (spec.get("paths") or {}).items():
        if isinstance(item, dict):
            for method in _METHODS:
                if isinstance(item.get(method), dict):
                    ops[f"{method.upper()} {path}"] = item[method]
    return ops


def describe(committed: dict[str, Any], expected: dict[str, Any]) -> str:
    """What moved, briefly: operations added, removed, changed, then schemas."""
    old, new = _operations(committed), _operations(expected)
    parts = []
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    for label, keys in (("added", added), ("removed", removed), ("changed", changed)):
        if keys:
            parts.append(f"{len(keys)} operation(s) {label} ({', '.join(keys[:3])}{', …' if len(keys) > 3 else ''})")
    old_s = (committed.get("components") or {}).get("schemas") or {}
    new_s = (expected.get("components") or {}).get("schemas") or {}
    schemas = sorted(k for k in set(old_s) | set(new_s) if old_s.get(k) != new_s.get(k))
    if schemas:
        parts.append(f"{len(schemas)} schema(s) differ ({', '.join(schemas[:3])}{', …' if len(schemas) > 3 else ''})")
    return "; ".join(parts) or "spec metadata differs"


def _committed_root(target: GenerationTarget) -> Path:
    """The consumer folder (what a repository commits); the Django-side copy when only that exists."""
    if (Path(target.path) / "openapi.json").is_file() or target.source_path is None:
        return Path(target.path)
    return Path(target.source_path)


def check_targets(targets: list[GenerationTarget], global_spec: dict[str, Any], config: OpenAPIConfig) -> list[str]:
    """One line per drifted or unreadable slice; empty = every target matches the schema."""
    problems: list[str] = []
    for target in targets:
        if target.tool in ("buf", "grpc-python"):
            continue
        root = _committed_root(target)
        for groups, folder in output_units(target, root):
            path = folder / "openapi.json"
            if not path.is_file():
                problems.append(f"{path}: missing (not generated yet?); run `make gen`")
                continue
            try:
                committed = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                problems.append(f"{path}: unreadable ({e})")
                continue
            try:
                expected = prepare_slice(target, groups, global_spec, config)
            except GeneratorError as e:
                problems.append(f"{target.name}: {e}")
                continue
            committed, expected = _comparable(committed), _comparable(expected)
            if committed != expected:
                problems.append(
                    f"{path}: the Django schema changed since it was generated: {describe(committed, expected)}; "
                    "run `make gen`"
                )
    return problems


def check_drift(config: OpenAPIConfig, targets: list[GenerationTarget]) -> list[str]:
    """Render the spec fresh (as ``run_pipeline`` does) and check every target against it."""
    from .orchestrator import _load_spec_cached

    cache = cache_dir(config)
    for name in ("global_spec.json", "global_spec.fingerprint"):
        (cache / name).unlink(missing_ok=True)
    report = RunReport()
    global_spec = _load_spec_cached(config, cache, targets, report)
    if global_spec is None:
        return [f"{name}: {err}" for name, err in report.failures]
    return check_targets(targets, global_spec, config)


__all__ = ["check_drift", "check_targets", "describe"]
