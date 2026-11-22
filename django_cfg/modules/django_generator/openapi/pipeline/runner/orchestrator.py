"""Top-level pipeline driver.

Owns the spec cache, fans targets out across a thread pool, and
publishes / mirrors successful outputs.

Two layers of caching feed in here:

* **Spec cache** (``cache.compute_spec_cache_key`` etc.) — replays the
  rendered OpenAPI document when nothing that affects it has changed.
  This is the single biggest cost on a non-trivial Django project.
* **Per-target cache** (consulted inside ``dispatch.run_single``) —
  replays the tool output snapshot when the sliced spec + tool config
  match a previous run.

The pool is sized via ``DJANGO_CFG_GEN_PARALLELISM`` (else
``min(8, cpu_count, target_count)``). Targets are independent — each
slices its own copy of the spec, writes to its own ``out_dir``, and
publishes to its own consumer path.
"""

from __future__ import annotations

import dataclasses
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ..cache import (
    compute_spec_cache_key,
    load_cached_spec,
    save_cached_spec,
)
from ..config import GenerationTarget, OpenAPIConfig, RunReport
from ..errors import GeneratorError
from ..postprocess import normalize_tags, warn_tag_format
from ..spec_loader import load_spec
from .dispatch import run_target
from ..staging import Stage
from .paths import (
    cache_dir,
    effective_root,
    find_project_root,
    mirror_target_to_tmp,
    stage_consumer,
)
from .progress import (
    now,
    print_run_summary,
    print_spec_status,
    print_target_result,
)


def run_pipeline(
    config: OpenAPIConfig,
    targets: list[GenerationTarget],
    *,
    dry_run: bool = False,
    force: bool = False,
) -> RunReport:
    """Generate every target. Each one is written to a staged copy of its
    output folder and swapped in only on success (``_run_staged``); ``force``
    lets the swap overwrite uncommitted changes the generator did not make."""
    report = RunReport()

    if not targets:
        return report

    if dry_run:
        report.targets_skipped.extend(t.name for t in targets)
        return report

    cache = cache_dir(config)
    run_started = now()

    # ════════════════════════════════════════════════════════════════════
    # ⚠️  CRITICAL — DO NOT REMOVE: per-run fingerprint invalidation
    # ════════════════════════════════════════════════════════════════════
    # Every `make gen` MUST nuke ALL fingerprint files in the cache so the
    # generators re-run end-to-end. Fingerprints only hash the SLICED SPEC
    # + tool config — they do NOT hash the generator's own Python source.
    # Without this wipe, edits to generator templates / post-processors go
    # undetected when the spec hasn't changed, and stale output ships.
    #
    # The per-target `fingerprint` is wiped for every external generator.
    # It covers the per-target snapshot cache (ogen / orval /
    #                             openapi-python-client / swift-openapi /
    #                             python post-processor)
    #
    # If you (an AI agent or human) "see this is unnecessary" — IT IS NOT.
    # The pain it prevents:
    #   - Generator template / post-process fixer edited → no spec change →
    #     cache says "hit" → tool isn't re-invoked → app keeps shipping
    #     stale output → 30 min of `find … -name fingerprint -delete`
    #     before the next `make gen` actually picks up the new code.
    #
    # This is the single source of truth for cache invalidation when
    # GENERATOR CODE changes.
    # ════════════════════════════════════════════════════════════════════
    for fp_name in ("fingerprint",):
        for fp in cache.rglob(fp_name):
            fp.unlink(missing_ok=True)

    # ════════════════════════════════════════════════════════════════════
    # Always nuke the spec cache so tag / schema / endpoint changes are
    # never masked.  The spec render is fast enough (~1-5 s) that the
    # safety of a guaranteed-fresh spec outweighs the cost.
    # ════════════════════════════════════════════════════════════════════
    if cache.exists():
        import shutil
        shutil.rmtree(cache)

    global_spec = _load_spec_cached(config, cache, targets, report)
    if global_spec is None:
        return report

    # Lint the spec for shapes that crash generated clients. Don't fail
    # the build — surface findings so engineers see them in `make gen`
    # output and have the option to act on them.
    from ..audit import audit_requestbody_content_types
    for finding in audit_requestbody_content_types(global_spec):
        print(finding.format())

    workers = _resolve_parallelism(len(targets))
    if workers <= 1 or len(targets) <= 1:
        # Sequential fallback — easier to debug, identical output.
        for target in targets:
            _process_one(target, global_spec, config, cache, report, force=force)
        _finalize(report, run_started)
        return report

    # Targets are independent: each slices a fresh copy of `global_spec`
    # into its own cache subdir and writes to its own `out_dir`. The
    # heavy lifting is external subprocess (ogen / orval / swift /
    # python-client) — Python time inside the worker is small, so a
    # ThreadPool releases the GIL during ``subprocess.run()`` and yields
    # ~Nx wallclock speedup for N tools running in parallel.
    started: dict[str, float] = {}

    def _submit(target: GenerationTarget):
        started[target.name] = now()
        return ex.submit(_run_staged, target, global_spec, config, cache, force)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="djcfg-gen") as ex:
        futures = {_submit(t): t for t in targets}
        for fut in as_completed(futures):
            target = futures[fut]
            elapsed = now() - started.get(target.name, now())
            try:
                ok, err, hit = fut.result()
            except Exception as exc:  # noqa: BLE001
                report.failures.append((target.name, f"{type(exc).__name__}: {exc}"))
                report.timings[target.name] = elapsed
                report.cache_hits[target.name] = False
                print_target_result(
                    target.name, ok=False, elapsed_s=elapsed,
                    cache_hit=False,
                    error=f"{type(exc).__name__}: {exc}",
                )
                continue

            report.timings[target.name] = elapsed
            report.cache_hits[target.name] = hit
            print_target_result(
                target.name, ok=ok, elapsed_s=elapsed,
                cache_hit=hit, error=err if not ok else None,
            )

            if ok:
                report.targets_run.append(target.name)
                if config.mirror_to_tmp:
                    mirror_target_to_tmp(target)
            else:
                report.failures.append((target.name, err or "unknown error"))

    _finalize(report, run_started)
    return report


def _finalize(report: RunReport, run_started: float) -> None:
    """Stamp the total wallclock and print the run-summary footer."""
    total = now() - run_started
    report.timings["__total__"] = total
    print_run_summary(
        total_s=total,
        timings=report.timings,
        cache_hits=report.cache_hits,
    )


def _load_spec_cached(
    config: OpenAPIConfig,
    cache: Path,
    targets: list[GenerationTarget],
    report: RunReport,
) -> dict[str, Any] | None:
    """Resolve the global OpenAPI spec via cache or fresh render.

    On cache hit: returns the stored dict (tag normalization already
    ran on it, so we skip that pass too). On miss: renders via
    ``load_spec``, normalizes tags, persists to cache. On render or
    postprocess failure: appends spec_load failures for every target
    and returns ``None``.
    """
    spec_key = compute_spec_cache_key(find_project_root(config.get_output_path()))
    started = now()
    cached = load_cached_spec(cache, spec_key)
    if cached is not None:
        elapsed = now() - started
        report.timings["__spec__"] = elapsed
        report.cache_hits["__spec__"] = True
        print_spec_status(cache_hit=True, elapsed_s=elapsed)
        return cached

    try:
        spec = load_spec()
    except GeneratorError as e:
        for t in targets:
            report.failures.append((t.name, f"spec_load: {e}"))
        return None

    # Tag enforcement is intentionally lenient for now — drf-spectacular
    # often emits tags via path-segment defaults. We only normalize.
    # Schema-name collisions are caught earlier inside
    # ``spec_loader.load_spec``.
    try:
        normalize_tags(spec)
        warn_tag_format(spec)
    except GeneratorError as e:
        for t in targets:
            report.failures.append((t.name, f"postprocess: {e}"))
        return None

    save_cached_spec(cache, spec_key, spec)
    elapsed = now() - started
    report.timings["__spec__"] = elapsed
    report.cache_hits["__spec__"] = False
    print_spec_status(cache_hit=False, elapsed_s=elapsed)
    return spec


def _process_one(
    target: GenerationTarget,
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
    cache: Path,
    report: RunReport,
    *,
    force: bool = False,
) -> None:
    """Sequential single-target step (used for parallelism=1)."""
    started = now()
    ok, err, hit = _run_staged(target, global_spec, config, cache, force)
    elapsed = now() - started
    report.timings[target.name] = elapsed
    report.cache_hits[target.name] = hit
    print_target_result(
        target.name, ok=ok, elapsed_s=elapsed,
        cache_hit=hit, error=err if not ok else None,
    )
    if ok:
        report.targets_run.append(target.name)
        if config.mirror_to_tmp:
            mirror_target_to_tmp(target)
    else:
        report.failures.append((target.name, err or "unknown error"))


def _run_staged(
    target: GenerationTarget,
    global_spec: dict[str, Any],
    config: OpenAPIConfig,
    cache: Path,
    force: bool,
) -> tuple[bool, str | None, bool]:
    """Run one target against a staged copy of its output folder.

    The tools clean their output folder before writing (``rmtree(out_dir)``,
    ``clean_stale_root``). They do it in a copy next to the real folder; the
    real folder (and, with ``source_path``, the consumer folder) is replaced
    only when the target succeeded and the git guard passed for both. On any
    failure both stay exactly as they were.
    """
    try:
        stage = Stage.open(effective_root(target))
    except GeneratorError as e:
        return False, str(e), False
    consumer: Stage | None = None
    try:
        if target.source_path is not None:
            staged = dataclasses.replace(target, source_path=stage.path)
        else:
            staged = dataclasses.replace(target, path=stage.path)
        ok, err, hit = run_target(staged, global_spec, config, cache)
        if not ok:
            stage.discard()
            return ok, err, hit
        try:
            consumer = stage_consumer(target, stage.path)
            stage.check(force=force)
            if consumer is not None:
                consumer.check(force=force)
            stage.commit(force=True)  # checked above, together with the consumer
            if consumer is not None:
                consumer.commit(force=True)
        except GeneratorError as e:
            stage.discard()
            if consumer is not None:
                consumer.discard()
            return False, str(e), hit
        return True, None, hit
    except BaseException:
        stage.discard()
        if consumer is not None:
            consumer.discard()
        raise


def _resolve_parallelism(target_count: int) -> int:
    """Pick worker count.

    Order:
      1. ``DJANGO_CFG_GEN_PARALLELISM`` env (set ``=1`` to disable
         parallelism when chasing a flaky tool or wanting clean serial
         logs).
      2. ``min(8, cpu_count, target_count)`` — most external generators
         are CPU-light from Python's POV (subprocess wait); 8 covers
         the largest target set we have.
    """
    env = os.environ.get("DJANGO_CFG_GEN_PARALLELISM")
    if env:
        try:
            return max(1, int(env))
        except ValueError:
            pass
    cpu = os.cpu_count() or 4
    return max(1, min(8, cpu, target_count))


__all__ = ["run_pipeline"]
