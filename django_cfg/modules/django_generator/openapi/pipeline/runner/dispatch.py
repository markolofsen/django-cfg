"""Per-target dispatch.

Two entry points:

* ``run_target`` — picks the layout policy (single output vs
  per-group split) and drives ``run_single`` for each slice.
* ``run_single`` — slices the spec, dispatches to the external tool,
  caches the output, runs ts_extras when needed.

The cache is consulted before the external tool runs and populated
after. A hit replays the stored snapshot into ``out_dir`` and the
external tool never runs.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ..cache import (
    _dict_hash,
    cache_disabled,
    compute_target_cache_key,
    restore_target_output,
    store_target_output,
)
from ..config import GenerationTarget, OpenAPIConfig
from ..errors import GeneratorError
from ..postprocess import nullable_3_1_to_3_0
from ..slicer import slice_by_tags
from ...groups.resolver import resolve_tags, resolve_tags_by_name
from ...tools.external import (
    buf_proto,
    grpc_python,
    hey_api,
    ogen,
    openapi_python_client,
    swift_openapi,
)
from ...tools.openapi_processor.python.tool import generate as generate_python_extras
from ...tools.openapi_processor.python.wrapper.generator import (
    generate as generate_python_wrapper,
    generate_barrel as generate_python_barrel,
)
from ...tools.openapi_processor.ts.tool import generate as generate_ts_extras
from .cache_keys import target_cache_slot, target_signature
from .paths import effective_root
from .ts_wrapper import clean_stale_root, run_ts_wrapper, ts_extras_list


def run_target(
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
      • TS targets (``hey-api``) render one sub-SDK per group into
        ``<target>/<group>/`` and emit a wrapper layer at ``<target>/``.
      • Other tools render flat for single-group targets, multi-group
        for the rest.
    """
    try:
        out_root = effective_root(target)
        proto_tool = target.tool in ("buf", "grpc-python")
        if proto_tool:
            ok, err, hit = run_single(target, target.groups, out_root, global_spec, config, cache)
            return ok, err, hit

        # TS targets: hey-api runs ONCE on the full spec into target_root/
        # (one sdk.gen.ts, one types.gen.ts, shared client/ core/).
        # ts_extras (zod schemas + SWR hooks) runs per-group with a
        # tag-sliced spec into target_root/_<group>/ so each group folder
        # contains only its own hooks and schemas.
        if target.tool == "hey-api":
            target_root = out_root
            groups_to_run = target.groups or ["default"]

            # Guard against group names that would conflict with hey-api SDK
            # output paths after the underscore prefix is prepended.
            _HEY_API_RESERVED = {
                "sdk.gen.ts", "types.gen.ts", "client.gen.ts",
                "client", "core", "helpers", "index.ts", "api.ts",
                "events.ts",
            }
            for _g in groups_to_run:
                _prefixed = f"_{_g}"
                if _prefixed in _HEY_API_RESERVED:
                    raise GeneratorError(
                        f"Group name {_prefixed!r} conflicts with hey-api SDK output "
                        f"— rename the group (reserved names: {sorted(_HEY_API_RESERVED)})"
                    )

            clean_stale_root(target_root, groups_to_run)

            # --- Step 1: single hey-api pass on union of all target groups ---
            # We slice to exactly the tags this target needs — cfg_* tags
            # won't bleed into a target that doesn't list them.
            sdk_cache = cache / "runs" / target.name / "__sdk__"
            sdk_cache.mkdir(parents=True, exist_ok=True)
            ok, err, sdk_hit = run_single(
                target,
                groups_to_run,   # union slice of all groups for this target
                target_root,
                global_spec,
                config,
                cache,
                cache_subdir=sdk_cache,
                _skip_ts_extras=True,  # ts_extras runs per-group below
            )
            if not ok:
                return False, f"hey-api (full spec): {err}", False

            # --- Step 2: ts_extras per group into <group>/ in parallel ---
            all_hit = sdk_hit
            extras = ts_extras_list(config)
            if extras:
                extras_key = "+".join(sorted(extras))

                def _run_group_extras(group_name: str) -> bool:
                    """Returns True if the group was served from cache."""
                    group_sliced = _resolve_and_slice(
                        target, [group_name], global_spec, config
                    )

                    if not group_sliced.get("paths"):
                        sep = "=" * 64
                        print(
                            f"\n{sep}\n"
                            f"  ⚠️  WARNING: group '{group_name}' matched 0 paths!\n"
                            f"  The OpenAPI tag in @extend_schema(tags=[...]) must match\n"
                            f"  the group name exactly (case-sensitive).\n"
                            f"  Expected tag string: '{group_name}'\n"
                            f"  Fix: update Django views so tags=['{group_name}'] everywhere.\n"
                            f"{sep}\n",
                            flush=True,
                        )

                    group_spec_cache = cache / "runs" / target.name / group_name
                    group_spec_cache.mkdir(parents=True, exist_ok=True)

                    # ts_extras output goes into target_root/_<group_name>/
                    # (underscore prefix keeps group dirs distinct from hey-api
                    # SDK files at the root).
                    group_out_dir = target_root / f"_{group_name}"

                    # Fingerprint: sliced spec + extras list + out_dir.
                    fp_input = {
                        "spec": group_sliced,
                        "extras": extras_key,
                        "out": group_out_dir.as_posix(),
                    }
                    fp = _dict_hash(fp_input)
                    fp_path = group_spec_cache / "extras.fingerprint"
                    if not cache_disabled() and fp_path.is_file():
                        try:
                            if fp_path.read_text(encoding="utf-8").strip() == fp:
                                return True  # cache hit — skip ts_extras
                        except OSError:
                            pass

                    group_spec_path = group_spec_cache / "openapi.json"
                    group_spec_path.write_text(
                        json.dumps(group_sliced, ensure_ascii=False, indent=2)
                    )
                    generate_ts_extras(
                        group_spec_path,
                        group_out_dir,
                        extras=extras,
                    )
                    try:
                        fp_path.write_text(fp, encoding="utf-8")
                    except OSError:
                        pass
                    return False

                group_hits: list[bool] = []
                workers = min(len(groups_to_run), 8)
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futs = {pool.submit(_run_group_extras, g): g for g in groups_to_run}
                    for fut in as_completed(futs):
                        exc = fut.exception()
                        if exc:
                            return False, f"{futs[fut]}: {exc}", False
                        group_hits.append(fut.result())
                all_hit = all_hit and all(group_hits)

            run_ts_wrapper(target, out_root)
            return True, None, all_hit

        # Other tools (ogen / openapi-python-client / swift-openapi):
        # single output, optional multi-group slice union.
        if len(target.groups) <= 1:
            ok, err, hit = run_single(target, target.groups, out_root, global_spec, config, cache)
            return ok, err, hit

        # Multi-group split for non-TS tools: keep legacy behavior.
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
    *,
    _skip_ts_extras: bool = False,
) -> tuple[bool, str | None, bool]:
    """Generate one SDK (one slice) into ``out_dir``.

    Returns ``(ok, err, cache_hit)`` — ``cache_hit`` is ``True`` when
    the per-target output cache served the result without invoking the
    external tool.
    """
    sliced = _resolve_and_slice(target, groups, global_spec, config)

    if target.tool == "ogen":
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
        return True, None, True

    ok, err = _dispatch_tool(target, spec_path, out_dir, config, skip_ts_extras=_skip_ts_extras)
    if not ok:
        return False, err, False

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
            allowed |= resolve_tags_by_name(group_name, global_spec)
    if target.tags:
        allowed |= set(target.tags)
    if not allowed:
        # No tags resolved → return a spec with empty paths rather than
        # the full spec. This prevents an unmatched group (e.g. an app
        # whose views carry no OpenAPI tags yet) from accidentally pulling
        # in *all* endpoints.
        empty = dict(global_spec)
        empty["paths"] = {}
        return empty
    return slice_by_tags(global_spec, allowed)


def _dispatch_tool(
    target: GenerationTarget,
    spec_path: Path,
    out_dir: Path,
    config: OpenAPIConfig,
    *,
    skip_ts_extras: bool = False,
) -> tuple[bool, str | None]:
    """Hand the sliced spec to the right external generator.

    Each branch is intentionally a thin shim — argument shapes already
    live in ``Target.options``; this function only validates them and
    forwards the call.
    """
    tool = target.tool
    options = target.options or {}

    if tool == "ogen":
        ogen.generate(spec_path, out_dir, package=str(options.get("package", "api")))
        return True, None

    if tool == "hey-api":
        client = str(options.get("client", "fetch"))
        plugins_opt = options.get("plugins")
        plugins = plugins_opt if isinstance(plugins_opt, list) else None
        hey_api.generate(spec_path, out_dir, client=client, plugins=plugins)
        if not skip_ts_extras:
            extras = ts_extras_list(config)
            if extras:
                generate_ts_extras(spec_path, out_dir, extras=extras)
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
        swift_openapi.generate(spec_path, out_dir, module_name=module)
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


__all__ = ["run_single", "run_target"]
