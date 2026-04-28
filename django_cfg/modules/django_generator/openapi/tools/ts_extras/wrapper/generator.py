"""Wrapper generator — per-group `class API` + shared utilities.

Architecture (matches legacy `api_old/` layout, adapted for Hey API + DRY):

    <target>/
      _shared/
        storage.ts            — Local/Memory/Cookie adapters (one copy)
        errors.ts             — APIError + NetworkError
        logger.ts             — APILogger (consola)
        validation-events.ts  — Zod CustomEvent dispatcher
      cfg_accounts/
        index.ts              — `class API` for this group + barrel re-exports
        client.gen.ts         — Hey API client (already there)
        sdk.gen.ts            — Hey API SDK classes (already there)
        types.gen.ts, zod.gen.ts, hooks/  (already there)
      cfg_totp/
        index.ts              — same shape, isolated `class API`
      cfg_centrifugo/
        index.ts              — same shape

Each group's `class API`:
  - takes `(baseUrl, { storage?, logger? })`
  - mounts only its own SDK classes as readonly props (`api.totp`, `api.totpSetup`, ...)
  - manages its own JWT via the storage adapter
  - wires Hey API request interceptor for Authorization: Bearer

Group `index.ts` re-exports `API`, storage adapters, errors, logger, validation
events — so consumers do `import { API, LocalStorageAdapter } from './generated/cfg_accounts'`.

The thin app-level `BaseClient.ts` (hand-written, not generated) instantiates one
`API` per group. See `_api/BaseClient.ts` in the solution.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .templates import (
    ERRORS_TS,
    LOGGER_TS,
    STORAGE_TS,
    VALIDATION_EVENTS_TS,
    render_group_api_ts,
    render_group_index_ts,
    render_target_index_ts,
)
from .templates.api import GroupSpec, OpRoute


_SDK_CLASS_RE = re.compile(r"export\s+class\s+([A-Z][A-Za-z0-9_]*)\b")


def _extract_sdk_classes(sdk_file: Path) -> list[str]:
    """Parse all SDK class names from a Hey API `sdk.gen.ts`.

    With `byTags` strategy Hey API emits one class per tag — multiple
    classes per file when a group covers several drf-spectacular tags.
    Deduplicate while preserving order: drf-spectacular slicing can
    leak the same tag into multiple positions of the same sdk file
    (rare, but observed); duplicates would later collide in the group
    `index.ts` re-export list.
    """
    try:
        text = sdk_file.read_text(encoding="utf-8")
    except OSError:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for name in _SDK_CLASS_RE.findall(text):
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


@dataclass(slots=True)
class WrapperResult:
    output_dir: Path
    files: list[Path] = field(default_factory=list)


def discover_group_dirs(target_dir: Path) -> list[tuple[str, list[GroupSpec]]]:
    """Walk `target_dir` and return `(dir_name, [GroupSpec, ...])` per group.

    One entry per per-group subdir that contains a Hey API `sdk.gen.ts`. The
    list of `GroupSpec` covers every `export class` in that file (one tag =
    one SDK class).
    """
    out: list[tuple[str, list[GroupSpec]]] = []
    for child in sorted(target_dir.iterdir()):
        if not child.is_dir() or child.name == "_shared":
            continue
        sdk_file = child / "sdk.gen.ts"
        if not sdk_file.exists():
            continue
        classes = _extract_sdk_classes(sdk_file)
        if not classes:
            continue
        specs = [GroupSpec(sdk_class=c, dir_name=child.name) for c in classes]
        out.append((child.name, specs))
    return out


def generate(
    target_dir: Path,
    *,
    access_key: str = "cfg.access_token",
    refresh_key: str = "cfg.refresh_token",
) -> WrapperResult:
    """Emit shared utilities + per-group `class API` wrapper.

    No-op (returns empty result) if no per-group SDKs are found.
    """
    target_dir = Path(target_dir)
    groups_by_dir = discover_group_dirs(target_dir)
    if not groups_by_dir:
        return WrapperResult(output_dir=target_dir)

    written: list[Path] = []

    # Shared utilities — one copy per target.
    shared_dir = target_dir / "_shared"
    shared_dir.mkdir(parents=True, exist_ok=True)
    written.append(_write(shared_dir / "storage.ts", STORAGE_TS))
    written.append(_write(shared_dir / "errors.ts", ERRORS_TS))
    written.append(_write(shared_dir / "logger.ts", LOGGER_TS))
    written.append(_write(shared_dir / "validation-events.ts", VALIDATION_EVENTS_TS))
    written.append(_write(shared_dir / "index.ts", _SHARED_BARREL))

    # Per-group: api.ts (class API) + index.ts (barrel).
    for dir_name, specs in groups_by_dir:
        group_dir = target_dir / dir_name
        routes = _read_routes(group_dir)
        written.append(_write(
            group_dir / "api.ts",
            render_group_api_ts(
                groups=specs,
                routes=routes,
                access_key=access_key,
                refresh_key=refresh_key,
            ),
        ))
        written.append(_write(
            group_dir / "index.ts",
            render_group_index_ts(groups=specs),
        ))

    # Top-level barrel — Next.js singletons + re-exports.
    written.append(_write(
        target_dir / "index.ts",
        render_target_index_ts(groups_by_dir=groups_by_dir),
    ))

    return WrapperResult(output_dir=target_dir, files=written)


_SHARED_BARREL = '''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Shared utilities barrel. DO NOT EDIT — re-run `make gen`.

export {
  type StorageAdapter,
  LocalStorageAdapter,
  MemoryStorageAdapter,
  CookieStorageAdapter,
} from './storage';
export { APIError, NetworkError } from './errors';
export {
  APILogger,
  defaultLogger,
  type LoggerConfig,
  type RequestLog,
  type ResponseLog,
  type ErrorLog,
} from './logger';
export {
  dispatchValidationError,
  onValidationError,
  formatZodError,
  type ValidationErrorDetail,
  type ValidationErrorEvent,
} from './validation-events';
'''


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _read_routes(group_dir: Path) -> list[OpRoute]:
    """Load `<group>/.routes.json` produced by ts_extras and convert
    entries to `OpRoute` instances. Missing file → empty list (the
    wrapper degrades gracefully to no auto-validation)."""
    path = group_dir / ".routes.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    routes: list[OpRoute] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        method = entry.get("method")
        path_pattern = entry.get("path")
        schema = entry.get("schema")
        if not method or not path_pattern:
            continue
        routes.append(OpRoute(method=method, path=path_pattern, schema=schema))
    return routes


__all__ = ["generate", "discover_group_dirs", "WrapperResult", "GroupSpec"]
