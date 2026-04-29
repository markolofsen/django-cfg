"""Wrapper generator — per-group `class API` + shared utilities.

Architecture (new layout — single shared SDK at target root):

    <target>/
      sdk.gen.ts            — SINGLE shared SDK (all groups combined), written by hey-api
      types.gen.ts          — SINGLE shared types, written by hey-api
      client/               — hey-api client
      core/                 — hey-api core
      helpers/
        storage.ts          — Local/Memory/Cookie adapters (one copy)
        errors.ts           — APIError + NetworkError
        logger.ts           — APILogger (consola)
        validation-events.ts — Zod CustomEvent dispatcher
        index.ts            — barrel re-export of above
      _skills/              — per-group subdir (underscore prefix, has hooks/ and/or schemas/)
        hooks/
        schemas/
        api.ts              — `class API` for this group
        index.ts            — barrel re-exports
      _reviews/
        hooks/
        schemas/
        api.ts
        index.ts

Each group's `class API`:
  - takes `(baseUrl, { storage?, logger? })`
  - mounts only its own SDK classes as readonly props (`api.totp`, `api.totpSetup`, ...)
  - manages its own JWT via the storage adapter
  - wires Hey API request interceptor for Authorization: Bearer

Group `index.ts` re-exports `API`, storage adapters, errors, logger, validation
events — so consumers do `import { API, LocalStorageAdapter } from './generated/_skills'`.

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
    render_auth_ts,
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

    One entry per per-group subdir (underscore-prefixed, e.g. ``_skills``)
    that contains a ``hooks/`` or ``schemas/`` directory produced by
    ts_extras. SDK classes are read from the **target root** ``sdk.gen.ts``
    (the single shared SDK written by hey-api), filtered to those whose
    name contains the group's logical name (strip leading underscore).
    """
    # Read the shared root sdk.gen.ts once.
    root_sdk_file = target_dir / "sdk.gen.ts"
    all_classes = _extract_sdk_classes(root_sdk_file)

    out: list[tuple[str, list[GroupSpec]]] = []
    for child in sorted(target_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in ("helpers", "client", "core", "_shared"):
            continue
        # Only consider underscore-prefixed group dirs that contain hooks/ or schemas/.
        if not child.name.startswith("_"):
            continue
        has_hooks = (child / "hooks").is_dir()
        has_schemas = (child / "schemas").is_dir()
        if not has_hooks and not has_schemas:
            continue
        # Derive the logical group name by stripping the leading underscore.
        logical_name = child.name[1:]
        # Filter SDK classes that belong to this group (case-insensitive prefix match).
        logical_lower = logical_name.lower().replace("_", "")
        group_classes = [
            c for c in all_classes
            if c.lower().startswith(logical_lower[:4]) or logical_lower in c.lower()
        ] if all_classes else []
        specs = [GroupSpec(sdk_class=c, dir_name=child.name) for c in group_classes]
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

    # Shared utilities — one copy per target, written to helpers/.
    helpers_dir = target_dir / "helpers"
    helpers_dir.mkdir(parents=True, exist_ok=True)
    written.append(_write(helpers_dir / "storage.ts", STORAGE_TS))
    written.append(_write(helpers_dir / "errors.ts", ERRORS_TS))
    written.append(_write(helpers_dir / "logger.ts", LOGGER_TS))
    written.append(_write(helpers_dir / "validation-events.ts", VALIDATION_EVENTS_TS))
    written.append(_write(
        helpers_dir / "auth.ts",
        render_auth_ts(access_key=access_key, refresh_key=refresh_key),
    ))
    written.append(_write(helpers_dir / "index.ts", _SHARED_BARREL))

    # Patch client.gen.ts so the auth interceptor installs as a
    # side-effect on first import — even when consumers only ever
    # touch hooks/SDK classes (which import client.gen directly,
    # bypassing index.ts).
    _ensure_auth_import_in_client(target_dir / "client.gen.ts")

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

export { auth, type Auth } from './auth';
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


_AUTH_IMPORT_MARKER = "// auto-init: install auth on client"
_AUTH_IMPORT_BLOCK = (
    f"{_AUTH_IMPORT_MARKER}\n"
    "import { installAuthOnClient } from './helpers/auth';\n"
    "installAuthOnClient(client);"
)


def _ensure_auth_import_in_client(client_gen: Path) -> None:
    """Append `installAuthOnClient(client)` to `client.gen.ts` if absent.

    `client.gen.ts` is written by hey-api on every run; we patch it
    after generation so the auth wiring runs synchronously right after
    `createClient()`. No circular import (auth.ts no longer imports
    `client`), no microtask deferral — this works for SSR where the
    first fetch can fire before any microtask is drained.
    """
    if not client_gen.exists():
        return
    text = client_gen.read_text(encoding="utf-8")
    if _AUTH_IMPORT_MARKER in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    text += f"\n{_AUTH_IMPORT_BLOCK}\n"
    client_gen.write_text(text, encoding="utf-8")


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
