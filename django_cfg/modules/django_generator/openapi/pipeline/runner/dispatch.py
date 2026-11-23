"""Per-target dispatch.

Two entry points:

* ``run_target`` — picks the layout policy (single output vs
  per-group split) and drives ``run_single`` for each slice.
* ``run_single`` — slices the spec, dispatches to the external tool,
  and caches the output.

The cache is consulted before the external tool runs and populated
after. A hit replays the stored snapshot into ``out_dir`` and the
external tool never runs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..cache import (
    compute_target_cache_key,
    restore_target_output,
    store_target_output,
)
from ..config import GenerationTarget, OpenAPIConfig
from ..errors import GeneratorError, SliceError
from ..postprocess import enforce_response_schemas, nullable_3_1_to_3_0
from ..slicer import _normalize_tag, slice_by_tags
from ...groups.resolver import resolve_tags, resolve_tags_by_name
from ..schema_refs import promote_inline_schemas
from ...tools.external import (
    buf_proto,
    grpc_python,
    ogen,
    openapi_python_client,
    orval,
    swift_openapi,
)
from ...tools.openapi_processor.go.tool import generate as generate_go_wrapper
from ...tools.openapi_processor.python.tool import generate as generate_python_extras
from ...tools.openapi_processor.python.wrapper.generator import (
    generate as generate_python_wrapper,
    generate_barrel as generate_python_barrel,
)
from .cache_keys import target_cache_slot, target_signature
from .paths import effective_root
from .stamp import stamp_info, stamp_target


def run_target(
    target: GenerationTarget,
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
    cache: Path,
) -> tuple[bool, str | None, bool]:
    """Dispatch a Target, then stamp it with the django-cfg that generated it (see ``stamp``)."""
    result = _run_target(target, global_spec, config, cache)
    if result[0]:
        stamp_target(effective_root(target))
    return result


def _run_target(
    target: GenerationTarget,
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
    cache: Path,
) -> tuple[bool, str | None, bool]:
    """Dispatch a Target. Returns ``(ok, err, fully_cached)``.

    ``fully_cached`` is ``True`` only when **every** ``run_single`` call
    for this target hit the per-target output cache — i.e. no external
    tool was invoked. Mixed runs (some groups hit, others miss) report
    ``False`` so the timing is interpreted correctly.

    Splitting policy:
      • Proto tools (``buf`` / ``grpc-python``) render flat into
        ``target.path``.
      • Orval TS targets render a clean React Query/Zod/MSW tree into the
        target root using ``tags-split``.
      • Other tools render flat for single-group targets, multi-group
        for the rest.
    """
    try:
        out_root = effective_root(target)
        proto_tool = target.tool in ("buf", "grpc-python")
        if proto_tool:
            ok, err, hit = run_single(target, target.groups, out_root, global_spec, config, cache)
            return ok, err, hit

        if target.tool == "orval":
            # Orval runs once on the union slice. Its tags-split mode creates
            # one endpoint module per OpenAPI tag and one shared model tree;
            # Orval owns the complete TypeScript output; no post-processor is involved.
            ok, err, hit = run_single(
                target,
                target.groups,
                out_root,
                global_spec,
                config,
                cache,
            )
            return ok, err, hit

        # Swift and TypeScript generators emit one module-level client from the
        # union of their selected groups. Splitting a Swift target produces
        # duplicate `Client`/`Components` declarations in the same SwiftPM
        # module; the group boundary belongs in the sliced spec, not the output
        # directory tree.
        if target.tool == "swift-openapi" or len(target.groups) <= 1:
            ok, err, hit = run_single(target, target.groups, out_root, global_spec, config, cache)
            return ok, err, hit

        # Multi-group split for ogen / openapi-python-client: keep legacy behavior.
        target_root = out_root
        all_hit = True
        for group_name in target.groups:
            sub_path = target_root / group_name
            sub_cache = cache / "runs" / target.name / group_name
            sub_cache.mkdir(parents=True, exist_ok=True)
            ok, err, hit = run_single(
                target,
                [group_name],
                sub_path,
                global_spec,
                config,
                cache,
                cache_subdir=sub_cache,
            )
            if not ok:
                return False, f"{group_name}: {err}", False
            all_hit = all_hit and hit
        # Python multi-group: emit a top-level __init__.py barrel that
        # re-exports every <Group>API, so app code can do
        #     from src._shared.api.generated import OperationsAPI
        # instead of fishing inside per-group wrapper modules.
        if target.tool == "openapi-python-client":
            generate_python_barrel(target_root)
        return True, None, all_hit
    except GeneratorError as e:
        return False, f"{type(e).__name__}: {e}", False
    except FileNotFoundError as e:
        return False, str(e), False
    except Exception as e:  # noqa: BLE001 — tool wrappers can throw anything
        return False, f"{type(e).__name__}: {e}", False


def run_single(
    target: GenerationTarget,
    groups: list[str],
    out_dir: Path,
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
    cache: Path,
    cache_subdir: Path | None = None,
) -> tuple[bool, str | None, bool]:
    """Generate one SDK (one slice) into ``out_dir``.

    Returns ``(ok, err, cache_hit)`` — ``cache_hit`` is ``True`` when
    the per-target output cache served the result without invoking the
    external tool.
    """
    sliced = _resolve_and_slice(target, groups, global_spec, config)
    promote_inline_schemas(sliced)
    if target.tool == "orval":
        # Before Orval: it types such an operation `unknown`, or refuses the spec without naming the view.
        enforce_response_schemas(sliced)
        # The banner Orval writes into every file reads `x-cfg-contract` from
        # `info`, so the slice is stamped before the tool runs and before the
        # cache key is taken (see ``stamp``). A copy of `info`: an empty slice
        # shares it with the global spec, which other targets read in parallel.
        if isinstance(sliced.get("info"), dict):
            sliced["info"] = dict(sliced["info"])
        stamp_info(sliced)

    if target.tool in ("ogen", "swift-openapi"):
        # ogen needs 3.0-style nullable; swift-openapi SILENTLY DROPS fields whose
        # schema is `anyOf:[{type:X},{type:null}]` (FastAPI/DRF Optional) unless they
        # are collapsed to `nullable:true` first. Same transform serves both.
        nullable_3_1_to_3_0(sliced)

    spec_dir = cache_subdir or (cache / "runs" / target.name)
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "openapi.json"
    spec_path.write_text(json.dumps(sliced, ensure_ascii=False, indent=2))

    out_dir = Path(out_dir)

    # Per-target output cache: most of the wallclock cost in this
    # function is the external tool boot + render. The output is a
    # pure function of (sliced spec, tool, tool options, target
    # signature) — when that fingerprint matches a previous run,
    # replay the cached snapshot into ``out_dir`` and skip the tool
    # entirely.
    target_key = compute_target_cache_key(
        sliced_spec=sliced,
        tool=target.tool,
        tool_options=dict(target.options or {}),
        target_signature=target_signature(target, groups, out_dir),
    )
    slot = target_cache_slot(target, groups)
    if restore_target_output(cache, slot, target_key, out_dir):
        # Cache hit: ogen output restored. Still run the Go wrapper so it
        # picks up any changes made to the post-processor itself.
        if target.tool == "ogen":
            pkg = str((target.options or {}).get("package", "api"))
            generate_go_wrapper(out_dir=out_dir, package=pkg)
        return True, None, True

    ok, err = _dispatch_tool(target, spec_path, out_dir, config)
    if not ok:
        return False, err, False

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "openapi.json").write_text(
        json.dumps(sliced, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Snapshot the freshly generated output for next run's cache lookup.
    store_target_output(cache, slot, target_key, out_dir)
    return True, None, False


def _resolve_and_slice(
    target: GenerationTarget,
    groups: list[str],
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
) -> dict[str, Any]:
    """Pick the tag set for ``groups`` and slice the global spec.

    A group with an explicit ``OpenAPIGroupConfig`` entry uses
    ``resolve_tags`` (apps-aware). A bare group name (passed via
    ``Target.groups`` without a paired config) falls back to
    ``resolve_tags_by_name``. ``Target.tags`` adds extra tags on top
    for ad-hoc filtering.
    """
    allowed: set[str] = set()
    for group_name in groups:
        group = next((g for g in config.groups if g.name == group_name), None)
        if group is not None:
            allowed |= resolve_tags(group, global_spec)
        else:
            tags = resolve_tags_by_name(group_name, global_spec)
            if not _tags_in_spec(tags, global_spec):
                raise SliceError(_unknown_group_message(target, group_name, config, global_spec))
            allowed |= tags
    if target.tags:
        allowed |= set(target.tags)
    if not allowed:
        # No tags resolved → return a spec with empty paths rather than
        # the full spec. This prevents an unmatched group (e.g. an app
        # whose views carry no OpenAPI tags yet) from accidentally pulling
        # in *all* endpoints.
        empty = dict(global_spec)
        empty["paths"] = {}
        empty.pop("x-realtime", None)  # no topics in this slice, so no key (see slicer.slice_by_tags)
        return empty
    return slice_by_tags(global_spec, allowed)


def _spec_tags(global_spec: dict[str, Any]) -> set[str]:
    """Every tag an operation or realtime topic carries, normalized as the slicer compares them."""
    found: set[str] = set()
    for item in (global_spec.get("paths") or {}).values():
        if isinstance(item, dict):
            for op in item.values():
                if isinstance(op, dict):
                    found.update(_normalize_tag(str(t)) for t in op.get("tags") or [])
    realtime = global_spec.get("x-realtime")
    if isinstance(realtime, dict):
        for topic in realtime.get("topics") or []:
            if isinstance(topic, dict):
                found.update(_normalize_tag(str(t)) for t in topic.get("tags") or [])
    return found


def _tags_in_spec(tags: set[str], global_spec: dict[str, Any]) -> bool:
    return bool({_normalize_tag(t) for t in tags} & _spec_tags(global_spec))


def _unknown_group_message(
    target: GenerationTarget, group_name: str, config: OpenAPIConfig, global_spec: dict[str, Any]
) -> str:
    """A group that is neither configured nor a tag: it would generate an empty client without a word."""
    configured = sorted(g.name for g in config.groups)
    near = sorted(t for t in _spec_tags(global_spec) if group_name.lower().rstrip("*_") in t)[:8]
    return (
        f"unknown group {group_name!r} in target {target.name} ({target.path}): it is not an OpenAPIGroupConfig "
        f"and no operation carries a tag for it, so the client would be empty. "
        f"Configured groups: {', '.join(configured) or 'none'}."
        + (f" Tags that look close: {', '.join(near)}." if near else "")
        + " Fix: correct the name in the Target's groups (generation.py), or add "
        f'OpenAPIGroupConfig(name="{group_name}", apps=[...]) to the openapi_client groups.'
    )


def _dispatch_tool(
    target: GenerationTarget,
    spec_path: Path,
    out_dir: Path,
    config: OpenAPIConfig,
) -> tuple[bool, str | None]:
    """Hand the sliced spec to the right external generator.

    Each branch is intentionally a thin shim — argument shapes already
    live in ``Target.options``; this function only validates them and
    forwards the call.
    """
    tool = target.tool
    options = target.options or {}

    if tool == "ogen":
        pkg = str(options.get("package", "api"))
        ogen.generate(spec_path, out_dir, package=pkg)
        generate_go_wrapper(out_dir=out_dir, package=pkg)
        return True, None

    if tool == "orval":
        workspace = _find_frontend_workspace(target.path)
        mock = options.get("mock", True)
        prettier = options.get("prettier", True)
        consumer_path = _consumer_path_for_stage(target.path)
        # The consumer folder, not ``out_dir``: with ``source_root`` the tree is
        # written inside the Django project, whose nearest package.json and
        # prettier config are not the frontend's.
        orval.generate(
            spec_path,
            out_dir,
            cwd=workspace,
            consumer_dir=consumer_path,
            mock=bool(mock),
            prettier=bool(prettier),
            runtime=runtime_import_for(consumer_path),
            auth_mode=str(options.get("auth_mode", "default")),
            direct_origin_tags=tuple(options.get("direct_origin_tags") or ()),
            infinite=bool(options.get("infinite", False)),
        )
        return True, None

    if tool == "openapi-python-client":
        pkg = options.get("package_name")
        openapi_python_client.generate(
            spec_path,
            out_dir,
            package_name=str(pkg) if isinstance(pkg, str) else None,
        )
        # Post-process: fix known upstream bugs (e.g. missing `Unset`
        # import when a function signature uses `| Unset = UNSET`).
        # Idempotent — safe to re-run.
        generate_python_extras(out_dir=out_dir)
        # Then emit a thin convenience wrapper class per tag-group:
        # ``<group>/wrapper.py`` exposing ``<Tag>API`` with ``set_token``
        # / ``set_api_key`` and one method per operation.
        generate_python_wrapper(out_dir=out_dir)
        return True, None

    if tool == "swift-openapi":
        module = str(options.get("module_name", "API"))
        access_mod = str(options.get("access_modifier", "public"))
        swift_openapi.generate(
            spec_path, out_dir, module_name=module, access_modifier=access_mod
        )
        return True, None

    if tool == "buf":
        proto_dir = options.get("proto_dir")
        if not isinstance(proto_dir, (str, Path)):
            return False, "buf target requires options.proto_dir"
        plugins_opt = options.get("plugins") or []
        plugins = list(plugins_opt) if isinstance(plugins_opt, list) else []
        plugin_options_raw = options.get("plugin_options") or {}
        plugin_options: dict[str, list[str]] = {}
        if isinstance(plugin_options_raw, dict):
            for k, v in plugin_options_raw.items():
                if isinstance(v, list):
                    plugin_options[str(k)] = [str(x) for x in v]
        buf_proto.generate(
            Path(proto_dir),
            out_dir,
            plugins=plugins,
            plugin_options=plugin_options,
        )
        return True, None

    if tool == "grpc-python":
        proto_dir = options.get("proto_dir")
        if not isinstance(proto_dir, (str, Path)):
            return False, "grpc-python target requires options.proto_dir"
        grpc_python.generate(Path(proto_dir), out_dir)
        return True, None

    return False, f"unknown tool: {tool}"


def runtime_import_for(consumer_path: Path) -> orval.RuntimeImport:
    """Where the generated mutator shim of the tree published to ``consumer_path`` imports the runtime from.

    * Default: the ``@djangocfg/api`` package root.
    * A hand-written ``runtime/orval-mutator.ts`` in an ancestor of the tree wins: a package that wraps the runtime
      (its own origin or headers) keeps doing so. The layout is not fixed (``packages/api/src/generated``,
      ``src/<group>/generated``), so every ancestor is checked. Such a file exports ``djangoFetch`` and
      ``DjangoRequestInit`` but not ``ApiClientError``, which then comes from the package.
    * Inside ``@djangocfg/api`` itself that ancestor is the runtime, and the package cannot import itself by name:
      everything comes relatively from that ``runtime`` folder's index.
    """
    consumer_path = Path(consumer_path)
    local_runtime = next(
        (
            candidate / "runtime" / "orval-mutator.ts"
            for candidate in consumer_path.parents
            if (candidate / "runtime" / "orval-mutator.ts").is_file()
        ),
        None,
    )
    if local_runtime is None:
        return orval.RuntimeImport(fetch=orval.RUNTIME_PACKAGE)
    shim_dir = consumer_path / "runtime"
    if _package_name(consumer_path) == orval.RUNTIME_PACKAGE:
        return orval.RuntimeImport(fetch=_relative_import(local_runtime.parent, shim_dir))
    return orval.RuntimeImport(
        fetch=_relative_import(local_runtime.with_suffix(""), shim_dir),
        errors=orval.RUNTIME_PACKAGE,
    )


def _relative_import(module: Path, start: Path) -> str:
    rel = Path(os.path.relpath(module, start=start)).as_posix()
    return rel if rel.startswith(".") else f"./{rel}"


def _package_name(consumer_path: Path) -> str | None:
    """The ``name`` of the ``package.json`` the consumer folder belongs to."""
    package_json = orval.consumer_package_json(consumer_path)
    if package_json is None:
        return None
    try:
        package = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = package.get("name") if isinstance(package, dict) else None
    return name if isinstance(name, str) else None


def _find_frontend_workspace(start: Path) -> Path:
    """Find the pnpm workspace that owns a generated TS target."""
    current = Path(start).resolve()
    candidates = [current, *current.parents]
    for directory in candidates:
        package_json = directory / "package.json"
        if not package_json.is_file():
            continue
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(package, dict) and package.get("workspaces"):
            return directory
        if (directory / "pnpm-workspace.yaml").is_file():
            return directory
    raise GeneratorError(
        f"could not find a pnpm workspace above TypeScript target {start}"
    )


def _consumer_path_for_stage(path: Path) -> Path:
    """Return the final output path when ``path`` is a staged target.

    Relative imports in generated files must be calculated from the path that
    will exist after the atomic stage swap, not from the temporary
    ``.<name>.djcfg-stage-*`` directory used while Orval runs.
    """
    path = Path(path)
    marker = f".{path.name}.djcfg-stage-"
    for parent in path.parents:
        if parent.name.startswith(marker):
            return parent.parent / path.name
    return path


__all__ = ["run_single", "run_target", "runtime_import_for"]
