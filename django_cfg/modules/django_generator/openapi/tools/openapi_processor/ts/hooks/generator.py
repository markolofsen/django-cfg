"""SWR hooks generator — orchestration only.

Layout (flat):
    hooks/<hookName>.ts            page-based query / mutation
    hooks/<hookName>Infinite.ts    infinite scroll variant (paginated only)
    hooks/index.ts                 barrel re-exporting every hook

Render logic lives in query.py / mutation.py / infinite_query.py / barrels.py.

For paginated endpoints (response ref starts with ``Paginated``) **both**
hooks are emitted:

    useApiKeysList          ← page-based useSWR — default for tables
    useApiKeysListInfinite  ← useSWRInfinite — for infinite-scroll feeds

For non-paginated GET endpoints only the regular query hook is emitted.
For non-GET methods only the mutation hook is emitted.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .barrels import render_flat_index
from .infinite_query import render_infinite_query
from .mutation import render_mutation
from .query import render_query
from ..ir import IR
from ..naming import hook_name

_QUERY_METHODS = {"get"}


def generate_hooks(ir: IR, out_dir: Path, *, sdk_import_prefix: str = "../..") -> list[Path]:
    """Emit one hook file per operation into ``out_dir``.

    ``sdk_import_prefix`` is the relative path from ``out_dir`` (the hooks
    dir) back to the directory holding hey-api's real ``sdk.gen.ts`` /
    ``types.gen.ts``. Per-group layout: ``"../.."`` (hooks at
    ``target_root/_<group>/hooks/``, SDK at ``target_root/``). Flat layout:
    ``".."`` (hooks at ``target_root/hooks/``, SDK at ``target_root/``).
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    files: list[Path] = []
    entries: list[tuple[str, str]] = []  # (file_name, hook_fn_name)

    for op in ir.operations:
        hook = hook_name(op.operation_id, method=op.method)

        if op.method in _QUERY_METHODS:
            # Always emit a page-based query hook for any GET (paginated or not).
            text = render_query(op, hook, sdk_import_prefix=sdk_import_prefix)
            file_name = f"{hook}.ts"
            (out_dir / file_name).write_text(text, encoding="utf-8")
            files.append(out_dir / file_name)
            entries.append((file_name, hook))

            # For paginated endpoints, additionally emit an infinite-scroll variant.
            if op.is_paginated:
                inf_hook = f"{hook}Infinite"
                inf_text = render_infinite_query(op, inf_hook, sdk_import_prefix=sdk_import_prefix)
                inf_file = f"{inf_hook}.ts"
                (out_dir / inf_file).write_text(inf_text, encoding="utf-8")
                files.append(out_dir / inf_file)
                entries.append((inf_file, inf_hook))
        else:
            text = render_mutation(op, hook, sdk_import_prefix=sdk_import_prefix)
            file_name = f"{hook}.ts"
            (out_dir / file_name).write_text(text, encoding="utf-8")
            files.append(out_dir / file_name)
            entries.append((file_name, hook))

    index_path = out_dir / "index.ts"
    index_path.write_text(render_flat_index(entries), encoding="utf-8")
    files.append(index_path)
    return files
