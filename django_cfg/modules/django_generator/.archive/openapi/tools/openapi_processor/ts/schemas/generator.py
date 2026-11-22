"""Zod schemas generator — orchestration only.

Layout:
    schemas/<Name>.ts       render.render_schema_file (zod expr from converter.to_zod)
    schemas/index.ts        render.render_index

Conversion lives in converter.py, ref-walking in refs.py, rendering in
render.py — this file just walks the IR and writes files.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path

from ..ir import IR, IRSchema
from ..naming import schema_filename
from .converter import to_zod
from .refs import collect_refs
from .render import (
    render_index,
    render_schema_file,
)

# drf-spectacular generates collision suffixes via:
#   f'{camelize(field_name)}{sha256(choices)[:3].capitalize()}Enum'
# The hash is exactly 3 hex chars. We pin to exactly 3 here; the guard
# (has_digit AND has_alpha) mirrors enum_naming.py so both modules agree
# on what counts as a mangled name.
#
# The regex is greedy on the base (`[A-Za-z0-9]+`) so it consumes as much
# as possible before the 3-char hex suffix — this prevents the lazy variant
# from eating real word characters into the hash group (e.g. "ce64b" from
# "Source64bEnum" with a lazy base).
_RE_HASH_SUFFIX = re.compile(
    r"^(?P<base>[A-Za-z][A-Za-z0-9]+)(?P<hash>[0-9a-fA-F]{3})Enum$"
)


def _split_hash_enum(name: str) -> tuple[str, str] | None:
    """Split ``<Base><Hash>Enum`` → ``(base, hash)`` for drf-spectacular
    collision-mangled names.

    Uses a greedy base group so the 3-char hex suffix is only what remains
    after consuming the longest valid base — avoiding false splits like
    ``Source64bEnum`` → (``Sour``, ``ce64b``).

    Any 3-char hex suffix is treated as a hash regardless of digit/alpha mix
    — ``Type370Enum`` (all-digit hash) is renamed just like ``StatusA3aEnum``.
    The only names excluded are ones with a stable suffix like plain
    ``StatusEnum`` (no hash) or ``ClientStatusEnum`` (``tus`` is hex but
    that's clearly a real word ending, not a hash — the greedy base consumes
    it all leaving nothing for the hash group).

    Examples:
        "StatusA3aEnum"    → ("Status", "A3a")
        "Source64bEnum"    → ("Source", "64b")
        "Status03aEnum"    → ("Status", "03a")
        "Type370Enum"      → ("Type",   "370")
        "StatusEnum"       → None  ← regex won't match (base needs 2+ chars)
        "ClientStatusEnum" → None  ← greedy base eats "ClientStatus", leaving
                                      only "tus" which is <3 chars after Enum
    """
    m = _RE_HASH_SUFFIX.match(name)
    if m is None:
        return None
    return m.group("base"), m.group("hash")



def _snake_to_pascal(s: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[_\-\s\.]+", s.strip()) if p)


def apply_enum_prefix(ir: IR, prefix: str) -> IR:
    """Return a new IR with all hash-suffixed enum names stabilised.

    Each colliding enum (e.g. ``StatusA3aEnum``) is renamed to
    ``<Prefix><BaseName>Enum`` (e.g. ``CrmStatusEnum`` when prefix is
    ``"crm"``). All ``$ref`` strings inside every schema's ``raw`` dict
    are updated to point to the new names.
    """
    if not prefix:
        return ir

    pascal_prefix = _snake_to_pascal(prefix)

    # Build rename map: old_name → new_name (only for hash-suffixed enums)
    rename: dict[str, str] = {}
    for name in ir.schemas:
        parts = _split_hash_enum(name)
        if parts is None:
            continue
        base, _ = parts
        new_name = f"{pascal_prefix}{base}Enum"
        if new_name != name:
            rename[name] = new_name

    if not rename:
        return ir  # nothing to do — skip copy

    # Serialise the whole IR.schemas to JSON once, do bulk string
    # replacement of all $ref values, then deserialise back.
    # This is safe because schema names are PascalCase identifiers —
    # they can't appear as substrings of other names.
    raw_json = json.dumps({k: v.raw for k, v in ir.schemas.items()})
    for old, new in rename.items():
        # Replace inside "$ref": "#/components/schemas/<old>"
        raw_json = raw_json.replace(
            f'"#/components/schemas/{old}"',
            f'"#/components/schemas/{new}"',
        )

    decoded: dict[str, dict] = json.loads(raw_json)

    new_schemas: dict[str, IRSchema] = {}
    for name in ir.schemas:
        new_name = rename.get(name, name)
        new_schemas[new_name] = IRSchema(name=new_name, raw=decoded[name])

    new_ir = copy.copy(ir)
    new_ir.schemas = new_schemas
    return new_ir


def generate_schemas(ir: IR, out_dir: Path, *, enum_prefix: str = "") -> list[Path]:
    if enum_prefix:
        ir = apply_enum_prefix(ir, enum_prefix)

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
