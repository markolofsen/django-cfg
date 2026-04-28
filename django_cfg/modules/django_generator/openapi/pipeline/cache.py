"""Fingerprint cache for the generation pipeline.

Two layers of cache, both fingerprint-based:

**1. Global spec cache.** ``drf-spectacular`` walks every URL pattern and
   renders an OpenAPI document — 5–15 seconds on a non-trivial Django
   project. The output only changes when serializers / views / urls
   change, so we hash a small set of inputs and reuse the rendered JSON
   when the hash matches.

**2. Per-target output cache.** A target's ``out_dir`` is a pure function
   of (sliced spec, tool, tool config). If we've already generated those
   bytes in a previous run, we can skip the entire ``ogen`` /
   ``hey-api`` / ``swift-openapi`` / ``openapi-python-client`` invocation.
   That's where most of the wallclock time lives — each tool boots a Go
   / Node / Python runtime, parses the spec, walks templates, writes
   files. None of that runs again on a clean cache hit.

Caches are per-project (live under ``openapi/.cache/``) and are
content-addressed: any change to inputs invalidates the relevant entry,
so manual cache busts are almost never necessary. To force a fresh
build, just ``rm -rf openapi/.cache``.

Set ``DJANGO_CFG_GEN_NO_CACHE=1`` to disable both layers (useful when
chasing a flaky tool — every target re-runs).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# Bump when changing the cache fingerprint algorithm or the runner's
# external-tool argument shape. Older cache entries silently miss.
_CACHE_FORMAT_VERSION = "v1"

# Files inside a Django project whose mtime is part of the spec
# fingerprint. We don't read every Python file in the project — that
# would be slow and noisy — only files known to influence the rendered
# OpenAPI document. Drf-spectacular itself contributes its installed
# version. Anything else (config tweaks, runtime data) is captured by
# explicit fingerprint inputs in `runner.py`.
_SPEC_FINGERPRINT_GLOBS = (
    "**/serializers.py",
    "**/serializers/*.py",
    "**/serializers/**/*.py",
    "**/views.py",
    "**/views/*.py",
    "**/views/**/*.py",
    "**/urls.py",
    "**/urls/*.py",
    "**/api/*.py",
    "**/api/**/*.py",
)

# Directories ignored when walking for spec fingerprint inputs.
_SKIP_DIRS = {
    ".venv", "venv", "node_modules", ".cache", "openapi", "@archive",
    "__pycache__", ".git", ".tox", "dist", "build", "media", "static",
    "logs", "@docs", "@dev", "@e2e", "@emails", "@rules",
}


def cache_disabled() -> bool:
    """Honour the env opt-out.

    The cache is on by default — opt-out is for debugging tool
    regressions where we want every target re-run end-to-end.
    """
    return os.environ.get("DJANGO_CFG_GEN_NO_CACHE") in {"1", "true", "yes"}


@dataclass(slots=True, frozen=True)
class SpecCacheKey:
    drf_spectacular_version: str
    settings_signature: str
    tree_signature: str

    def hash(self) -> str:
        h = hashlib.sha256()
        h.update(_CACHE_FORMAT_VERSION.encode())
        h.update(b"\x00")
        h.update(self.drf_spectacular_version.encode())
        h.update(b"\x00")
        h.update(self.settings_signature.encode())
        h.update(b"\x00")
        h.update(self.tree_signature.encode())
        return h.hexdigest()


def compute_spec_cache_key(project_root: Path) -> SpecCacheKey:
    """Build a fingerprint that changes whenever a re-render of the
    OpenAPI spec is *necessary*.

    Inputs:
      - ``drf-spectacular`` package version (catches library upgrades).
      - A snapshot of the ``SPECTACULAR_SETTINGS`` dict (catches
        ``ENUM_NAME_OVERRIDES`` edits, hook changes, etc.).
      - ``mtime + size`` of every file matching the serializer / view /
        urls globs under ``project_root`` (catches Django code edits).

    The third input is intentionally coarse-grained — we miss e.g. a
    ``@extend_schema`` decorator added inside a viewset that doesn't live
    in one of the globbed paths. If that becomes a real source of stale
    caches we widen the globs (or the user runs with cache off).
    """
    return SpecCacheKey(
        drf_spectacular_version=_get_drf_version(),
        settings_signature=_settings_signature(),
        tree_signature=_tree_signature(project_root),
    )


def load_cached_spec(cache_dir: Path, key: SpecCacheKey) -> dict[str, Any] | None:
    if cache_disabled():
        return None
    fp_path = cache_dir / "global_spec.fingerprint"
    spec_path = cache_dir / "global_spec.json"
    if not fp_path.is_file() or not spec_path.is_file():
        return None
    try:
        if fp_path.read_text(encoding="utf-8").strip() != key.hash():
            return None
        return json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_cached_spec(cache_dir: Path, key: SpecCacheKey, spec: dict[str, Any]) -> None:
    if cache_disabled():
        return
    cache_dir.mkdir(parents=True, exist_ok=True)
    spec_path = cache_dir / "global_spec.json"
    fp_path = cache_dir / "global_spec.fingerprint"
    try:
        spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        fp_path.write_text(key.hash(), encoding="utf-8")
    except OSError:
        # Cache failure is never fatal.
        pass


@dataclass(slots=True, frozen=True)
class TargetCacheKey:
    sliced_spec_hash: str
    tool: str
    tool_options_hash: str
    target_signature: str

    def hash(self) -> str:
        h = hashlib.sha256()
        h.update(_CACHE_FORMAT_VERSION.encode())
        h.update(b"\x00")
        h.update(self.sliced_spec_hash.encode())
        h.update(b"\x00")
        h.update(self.tool.encode())
        h.update(b"\x00")
        h.update(self.tool_options_hash.encode())
        h.update(b"\x00")
        h.update(self.target_signature.encode())
        return h.hexdigest()


def compute_target_cache_key(
    *,
    sliced_spec: dict[str, Any],
    tool: str,
    tool_options: dict[str, Any],
    target_signature: str,
) -> TargetCacheKey:
    return TargetCacheKey(
        sliced_spec_hash=_dict_hash(sliced_spec),
        tool=tool,
        tool_options_hash=_dict_hash(tool_options),
        target_signature=target_signature,
    )


def target_cache_dir(cache_root: Path, target_name: str) -> Path:
    """Per-target cached output snapshot directory."""
    return cache_root / "outputs" / target_name


def restore_target_output(
    cache_root: Path, target_name: str, key: TargetCacheKey, dest: Path
) -> bool:
    """If a cached output for ``key`` exists, copy it to ``dest`` and
    return ``True``. Otherwise return ``False`` and leave ``dest``
    untouched.

    Used by the runner before invoking the external tool — a hit means
    we skip the entire ogen / hey-api / swift / python-client run.
    """
    if cache_disabled():
        return False
    cache_dir = target_cache_dir(cache_root, target_name)
    fp_path = cache_dir / "fingerprint"
    snapshot = cache_dir / "snapshot"
    if not fp_path.is_file() or not snapshot.is_dir():
        return False
    try:
        if fp_path.read_text(encoding="utf-8").strip() != key.hash():
            return False
    except OSError:
        return False
    # Hit — replay the snapshot into the live target dir.
    try:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(snapshot, dest)
    except OSError:
        return False
    return True


def store_target_output(
    cache_root: Path, target_name: str, key: TargetCacheKey, source: Path
) -> None:
    """Copy ``source`` (the freshly generated tool output) into the
    per-target cache snapshot keyed by ``key``."""
    if cache_disabled():
        return
    cache_dir = target_cache_dir(cache_root, target_name)
    snapshot = cache_dir / "snapshot"
    fp_path = cache_dir / "fingerprint"
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        if snapshot.exists():
            shutil.rmtree(snapshot)
        shutil.copytree(source, snapshot)
        fp_path.write_text(key.hash(), encoding="utf-8")
    except OSError:
        # Best-effort caching — don't fail the build because of it.
        pass


def _dict_hash(payload: Any) -> str:
    """Stable hash of an arbitrary JSON-serialisable payload.

    ``sort_keys=True`` ensures dict ordering doesn't perturb the hash;
    ``default=str`` lets us hash sets/Path objects without exploding.
    """
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _get_drf_version() -> str:
    try:
        import drf_spectacular  # noqa: WPS433 — runtime import is the point.

        return getattr(drf_spectacular, "__version__", "unknown")
    except Exception:  # pragma: no cover — drf-spectacular missing == bigger problem
        return "missing"


def _settings_signature() -> str:
    """Hash the SPECTACULAR_SETTINGS dict (and a couple of related
    knobs) to invalidate the cache on user-config edits.

    Anything inside SPECTACULAR_SETTINGS counts: enum overrides,
    POSTPROCESSING_HOOKS, OAS_VERSION, etc. Best-effort — we bail to a
    constant signature when Django isn't ready yet, which is safe (the
    spec hash will still differ for any other reason that should
    invalidate).
    """
    try:
        from django.conf import settings  # local import — Django may be mid-boot
    except Exception:
        return "no-django"
    try:
        spec = dict(getattr(settings, "SPECTACULAR_SETTINGS", {}) or {})
        # POSTPROCESSING_HOOKS may contain function objects when set
        # programmatically — coerce to str so json.dumps survives.
        hooks = spec.get("POSTPROCESSING_HOOKS")
        if hooks is not None:
            spec["POSTPROCESSING_HOOKS"] = [str(h) for h in hooks]
        policy = getattr(settings, "DJANGO_CFG_ENUM_COLLISION_POLICY", "")
        return _dict_hash({"spec": spec, "policy": policy})
    except Exception:
        return "settings-error"


def _tree_signature(project_root: Path) -> str:
    """Hash relpath + mtime + size for every file matching our globs.

    We deliberately avoid reading file contents — mtime + size is a
    stable enough proxy and orders of magnitude faster on a project of
    several hundred Python files. False-positive cache invalidations
    (touching a file without editing it) are cheap; false-negative
    misses (real edit not detected) would be silent. The globs target
    only files that influence the OpenAPI render.
    """
    parts: list[tuple[str, float, int]] = []
    seen: set[Path] = set()
    for entry in _walk(project_root):
        if entry in seen:
            continue
        seen.add(entry)
        try:
            stat = entry.stat()
        except OSError:
            continue
        try:
            rel = entry.relative_to(project_root).as_posix()
        except ValueError:
            rel = str(entry)
        parts.append((rel, stat.st_mtime, stat.st_size))
    parts.sort()
    return _dict_hash(parts)


def _walk(project_root: Path) -> Iterable[Path]:
    for pattern in _SPEC_FINGERPRINT_GLOBS:
        for p in project_root.glob(pattern):
            if not p.is_file():
                continue
            if _is_skipped(p, project_root):
                continue
            yield p


def _is_skipped(path: Path, project_root: Path) -> bool:
    try:
        rel_parts = path.relative_to(project_root).parts
    except ValueError:
        return False
    return any(part in _SKIP_DIRS for part in rel_parts)


__all__ = [
    "SpecCacheKey",
    "TargetCacheKey",
    "cache_disabled",
    "compute_spec_cache_key",
    "compute_target_cache_key",
    "load_cached_spec",
    "restore_target_output",
    "save_cached_spec",
    "store_target_output",
    "target_cache_dir",
]


# Silence unused-import warning if `subprocess` / `sys` get repurposed.
_ = (subprocess, sys)
