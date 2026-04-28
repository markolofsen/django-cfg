"""Zod schemas generator — flat layout, deduped by name.

Layout:
    schemas/<Name>.ts       one file per `components.schemas` entry
    schemas/index.ts        barrel re-exporting every schema

Schemas are flat by design: zod schemas are tied to data shapes, not to
operations or tags. The same `User` may be referenced from many tags
without copying — and Hey API's `types.gen.ts` already provides a single
TypeScript type per shape. Duplicate names across Django apps are caught
upstream by `pipeline.postprocess.enforce_unique_schemas`, so by the time
we get here the spec is conflict-free.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..ir import IR
from ..naming import schema_filename
from .converter import to_zod
from .refs import collect_refs
from .render import render_schema_file, render_tag_index


def generate_schemas(ir: IR, out_dir: Path) -> list[Path]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    files: list[Path] = []
    names = sorted(ir.schemas)

    def has(name: str) -> bool:
        return name in ir.schemas

    for name in names:
        schema = ir.schemas[name]
        body = to_zod(schema.raw, lookup=has)
        deps = [
            (d, f"./{d}")
            for d in sorted(collect_refs(schema.raw) - {name})
            if has(d)
        ]
        text = render_schema_file(name=name, body=body, deps=deps)
        path = out_dir / schema_filename(name)
        path.write_text(text, encoding="utf-8")
        files.append(path)

    index_path = out_dir / "index.ts"
    index_path.write_text(render_tag_index(names), encoding="utf-8")
    files.append(index_path)
    return files
