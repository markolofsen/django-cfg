"""SWR hooks generator — orchestration only.

Layout (flat — group dir already segments by tag at the SDK level):
    <group>/hooks/<hookName>.ts   query.render_query / mutation.render_mutation
    <group>/hooks/index.ts        barrels.render_flat_index

Render logic lives in query.py / mutation.py / barrels.py — this file just
walks the IR, dispatches by HTTP method, and writes files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .barrels import render_flat_index
from .mutation import render_mutation
from .query import render_query
from ..ir import IR
from ..naming import hook_name

_QUERY_METHODS = {"get"}


def generate_hooks(ir: IR, out_dir: Path) -> list[Path]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    files: list[Path] = []
    entries: list[tuple[str, str]] = []
    for op in ir.operations:
        hook = hook_name(op.operation_id, method=op.method)
        text = (
            render_query(op, hook)
            if op.method in _QUERY_METHODS
            else render_mutation(op, hook)
        )
        file_name = f"{hook}.ts"
        (out_dir / file_name).write_text(text, encoding="utf-8")
        files.append(out_dir / file_name)
        entries.append((file_name, hook))

    index_path = out_dir / "index.ts"
    index_path.write_text(render_flat_index(entries), encoding="utf-8")
    files.append(index_path)
    return files
