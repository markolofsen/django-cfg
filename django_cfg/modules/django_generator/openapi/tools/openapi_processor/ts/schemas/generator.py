"""Zod schemas generator — orchestration only.

Layout:
    schemas/<Name>.ts       render.render_schema_file (zod expr from converter.to_zod)
    schemas/index.ts        render.render_index

Conversion lives in converter.py, ref-walking in refs.py, rendering in
render.py — this file just walks the IR and writes files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..ir import IR
from ..naming import schema_filename
from .converter import to_zod
from .refs import collect_refs
from .render import (
    render_index,
    render_schema_file,
)


def generate_schemas(ir: IR, out_dir: Path) -> list[Path]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    files: list[Path] = []
    names = sorted(ir.schemas.keys())

    def has(name: str) -> bool:
        return name in ir.schemas

    for name in names:
        schema = ir.schemas[name]
        body = to_zod(schema.raw, lookup=has)
        deps = sorted(d for d in collect_refs(schema.raw) - {name} if has(d))

        text = render_schema_file(name=name, body=body, deps=deps)
        path = out_dir / schema_filename(name)
        path.write_text(text, encoding="utf-8")
        files.append(path)

    index_path = out_dir / "index.ts"
    index_path.write_text(render_index(names), encoding="utf-8")
    files.append(index_path)
    return files
