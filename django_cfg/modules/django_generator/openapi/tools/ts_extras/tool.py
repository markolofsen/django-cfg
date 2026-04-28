"""ts_extras entry point.

Reads a (sliced) OpenAPI spec and emits zod schemas + SWR hooks +
the events bridge file into subfolders of `out_dir`. Intended to run
after Hey API has produced models + client into the same `out_dir`.

Outputs:
    out_dir/schemas/<SchemaName>.ts
    out_dir/schemas/index.ts
    out_dir/hooks/<tag>/<hookName>.ts
    out_dir/hooks/<tag>/index.ts
    out_dir/hooks/index.ts
    out_dir/events.ts
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .events.generator import generate_events
from .hooks.generator import generate_hooks
from .ir import build_ir
from .schemas.generator import generate_schemas


@dataclass(slots=True)
class TsExtrasResult:
    output_dir: Path
    files: list[Path] = field(default_factory=list)


def generate(spec_path: Path, out_dir: Path, *, extras: list[str]) -> TsExtrasResult:
    """Generate the requested extras into `out_dir`.

    `extras` selects which sub-generators run: {"zod", "hooks", "events"}.
    Order is fixed: zod → hooks → events (events is purely additive, no
    cross-deps).
    """
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    ir = build_ir(spec)
    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[Path] = []
    if "zod" in extras:
        files.extend(generate_schemas(ir, out_dir / "schemas"))
    if "hooks" in extras:
        files.extend(generate_hooks(ir, out_dir / "hooks"))
    if "events" in extras:
        files.extend(generate_events(out_dir))

    # Sidecar route → response-schema map for the wrapper's response
    # interceptor (auto zod validation). Always written so the wrapper
    # can rely on its presence.
    routes = [
        {
            "method": op.method.upper(),
            "path": op.path,
            "schema": op.response_schema_ref,
        }
        for op in ir.operations
    ]
    routes_path = out_dir / ".routes.json"
    routes_path.write_text(json.dumps(routes, ensure_ascii=False, indent=2), encoding="utf-8")
    files.append(routes_path)

    return TsExtrasResult(output_dir=out_dir, files=files)
