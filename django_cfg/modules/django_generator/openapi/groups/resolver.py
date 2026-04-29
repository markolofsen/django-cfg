"""Resolve a group name → OpenAPI tag set.

Tag scheme (deterministic, no path heuristics):

  django-cfg ops always carry **two** tags:
      ["cfg", "<app>"]              # auto-stamped by PathBasedAutoSchema
                                    # for /cfg/<app>/... URLs
      ["cfg", "<app>", "<custom>"]  # when `extend_schema(tags=[...])` adds
                                    # human-readable Swagger groupings

  App-side ops (non-cfg) carry app/feature tags:
      ["Profiles"], ["Crypto"], …

Resolution rules (first match wins):

  1. Explicit `OpenAPIGroupConfig.tags` → use verbatim.
  2. `cfg_<x>` group → ops with `{"cfg", "<x>"}` ⊆ tags. The auto-stamped
     pair guarantees the match. Custom Swagger tags ride along for free.
  3. App-side group with `apps=["apps.<X>"]` → ops where any tag matches
     `<X>` (case-insensitive) AND the op is **not** a django-cfg op
     (i.e. `"cfg"` not in tags) — keeps demo `profiles` from dragging in
     `cfg:accounts`.

Globs (`cfg_*`) collect every `<x>` after the `cfg:` prefix.
"""

from __future__ import annotations

import fnmatch
from typing import Any

from ..pipeline.config import OpenAPIGroupConfig

_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_CFG_PREFIX = "cfg_"
_CFG_MARKER = "cfg"


def resolve_tags(
    group: OpenAPIGroupConfig,
    global_spec: dict[str, Any],
) -> set[str]:
    if group.tags:
        return set(group.tags)

    short_names: set[str] = set()
    for app in group.apps:
        short = app.split(".")[-1]
        short_names.add(short.lower())

    found: set[str] = set()
    for op in _iter_ops(global_spec):
        tags = [str(t) for t in (op.get("tags") or [])]
        if _CFG_MARKER in tags:
            # django-cfg op — never claim it for app-side groups.
            continue
        if any(t.lower() in short_names for t in tags):
            found.update(tags)
    return found


def resolve_tags_by_name(
    group_name: str,
    global_spec: dict[str, Any],
) -> set[str]:
    """Derive tag set from a group name alone (no `OpenAPIGroupConfig`)."""
    if group_name.startswith(_CFG_PREFIX):
        inner = group_name[len(_CFG_PREFIX):]  # "accounts" or "*"
        return _collect_cfg_tags(global_spec, sub_glob=inner)

    # Non-cfg fallback: group name itself is the tag.
    return {group_name}


def _collect_cfg_tags(global_spec: dict[str, Any], *, sub_glob: str) -> set[str]:
    """Collect tags identifying ops where `{"cfg", <sub>}` ⊆ tags and
    `<sub>` matches `sub_glob`.

    Returns the set of **non-cfg** tags found on matching ops — the
    bare `"cfg"` marker is shared by every django-cfg op, so including
    it in the slice filter would re-collect every other group too.

    With `sub_glob == "*"` this gathers all django-cfg sub-tags (used
    for `cfg_*` glob groups).
    """
    found: set[str] = set()
    for op in _iter_ops(global_spec):
        tags = [str(t) for t in (op.get("tags") or [])]
        if _CFG_MARKER not in tags:
            continue
        sub_tags = [t for t in tags if t != _CFG_MARKER]
        if any(fnmatch.fnmatch(t, sub_glob) for t in sub_tags):
            found.update(sub_tags)
    return found


def _iter_ops(global_spec: dict[str, Any]):
    paths: dict[str, Any] = global_spec.get("paths", {})
    for _path, item in list(paths.items()):
        if not isinstance(item, dict):
            continue
        for method, op in list(item.items()):
            if method.lower() in _HTTP_METHODS and isinstance(op, dict):
                yield op


__all__ = ["resolve_tags", "resolve_tags_by_name"]
