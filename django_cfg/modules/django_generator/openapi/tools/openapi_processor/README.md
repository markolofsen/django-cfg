# openapi_processor

**Portable post-processor for OpenAPI-generated SDKs.**

Drop this entire folder into any generator package — it has zero external
Python dependencies and no project-specific imports. Point it at a different
OpenAPI spec and get the same output structure.

---

## Concept

Code generators like `@hey-api/openapi-ts` produce a raw SDK: types, a fetch
client, class-per-tag methods. They stop there by design. `openapi_processor`
is the second pass that adds the production layer every real app needs —
runtime validation, React hooks, a typed realtime bridge, and `class API`
wrappers with JWT management.

The two passes share no state. The generator writes `sdk.gen.ts` and
`types.gen.ts` to the target directory. `openapi_processor` then writes only
into `_<group>/` subdirs and `helpers/` — it never touches the generated SDK
files.

---

## Structure

```
openapi_processor/
  README.md         ← this file
  __init__.py
  ts/               ← TypeScript post-processor
    README.md
    ir.py
    naming.py
    tool.py
    hooks/          ← query.py + mutation.py + infinite_query.py + generator.py + barrels.py
    schemas/        ← OpenAPI → Zod generator
    events/         ← Centrifugo channel bridge
    wrapper/        ← class API + helpers + top-level barrel
  tests/
    ts/             ← pytest suite (112 tests)
```

Sub-processors are organized by output language. Today only `ts/` exists.
Adding `py/` or `kotlin/` in the future means dropping a new subfolder here
— the contract is identical.

---

## Sub-processors

### `ts/` — TypeScript

Post-processes `@hey-api/openapi-ts` output. Reads a sliced OpenAPI 3.1
spec and emits:

| Output | What |
|---|---|
| `_<group>/schemas/` | Zod schemas for every component schema |
| `_<group>/hooks/` | SWR hooks per operation (flat, one file per hook). Paginated GET endpoints get **both** a page-based `useSWR` hook and a `<hook>Infinite` `useSWRInfinite` variant side-by-side; non-paginated GET → single query hook; non-GET → mutation. |
| `_<group>/sdk.gen.ts` / `_<group>/types.gen.ts` | Re-export shims pointing at the top-level Hey API SDK so app code can import classes/types via the group-scoped path |
| `_<group>/events.ts` | Centrifugo channel → TS type bridge |
| `_<group>/api.ts` | `class API` with JWT interceptor + Zod validation routes |
| `_<group>/index.ts` | Barrel re-export |
| `helpers/` | `StorageAdapter`, `APIError`, `APILogger`, Zod event dispatcher |
| `index.ts` | Top-level barrel with Next.js-safe singletons |

See `ts/README.md` for full architecture and usage.

---

## Validation guards (in `ts/ir.py`)

`build_ir()` enforces these rules before emitting any output:

| Rule | Behaviour |
|---|---|
| Endpoint has no tag | `ValueError` — generator stops |
| Duplicate `operationId` | `ValueError` — lists both paths |
| `DELETE` with `requestBody` | `ValueError` — suggests `@extend_schema(request=None)` |
| Inline schema (no `$ref`) | `WARNING` — schema ignored, generation continues |
| Dangling `$ref` (schema absent from `components.schemas`) | `WARNING` — Hey API still uses the name, zod skipped |

---

## Cache: fingerprint auto-invalidation

Each generation run **wipes** every `extras.fingerprint` file in the cache
before any group-level work starts. This guarantees ts_extras re-runs
end-to-end whenever generator templates change — the per-group fingerprint
hashes only the sliced spec + extras list, not the templates themselves.

The wipe lives in:

- `pipeline/runner/orchestrator.py` (djangocfg)
- `core/runner.py` (cmdop_server mirror)

Both call sites carry a loud "DO NOT REMOVE" comment block. If you (an
AI agent or human) think the wipe is redundant — **it is not**. Without
it, edits to `query.py` / `mutation.py` / `infinite_query.py` / `tool.py`
get masked when the OpenAPI spec hasn't changed, and stale hooks ship.

---

## Tag mismatch warning (in runner)

When a group is sliced from the global spec and produces **0 paths**, the
runner prints a loud warning before continuing:

```
================================================================
  ⚠️  WARNING: group 'api_keys' matched 0 paths!
  The OpenAPI tag in @extend_schema(tags=[...]) must match
  the group name exactly (case-sensitive).
  Expected tag string: 'api_keys'
  Fix: update Django views so tags=['api_keys'] everywhere.
================================================================
```

This almost always means the Django view uses a human-readable tag
(`"API Keys"`) while the generation config uses a snake_case group name
(`"api_keys"`). Fix: change `@extend_schema(tags=["API Keys"])` →
`@extend_schema(tags=["api_keys"])` in all views for that group.

---

## Tests

```bash
# djangocfg
uv run pytest src/django_cfg/modules/django_generator/openapi/tools/openapi_processor/tests/ts/ -v

# cmdop_server
cd opensource && uv run pytest src/devtools/generator/tools/openapi_processor/tests/ts/ -v
```

112 tests covering IR validation, naming helpers (`_hey_api_camel`,
`_hey_api_pascal`, `sdk_class_name`, `sdk_fn_name`, `sdk_type_names`),
hook render output (`render_query`, `render_mutation`, `render_paginated_query`),
param handling, and paginated hook shape.

---

## How to copy

```bash
rsync -av --delete --exclude='__pycache__' \
  openapi_processor/ \
  /path/to/other/generator/tools/openapi_processor/
```

Then in your `runner.py`:

```python
from <your_package>.tools.openapi_processor.ts.tool import generate as generate_ts_extras
from <your_package>.tools.openapi_processor.ts.wrapper.generator import generate as generate_ts_wrapper
```

That is the only wiring needed. The module discovers group dirs, reads
`sdk.gen.ts`, and writes all output automatically.

---

## Portability guarantees

- **Zero external Python deps** — stdlib only (`pathlib`, `json`, `re`,
  `dataclasses`, `collections`).
- **No project-specific imports** — no Django, FastAPI, or host-package
  references anywhere inside this folder.
- **Idempotent** — re-running with the same spec produces identical output.
  Safe to commit generated files and diff them in CI.
- **Backend-agnostic** — same module runs against Django (drf-spectacular)
  and FastAPI (fastapi-users / custom) specs without modification.

---

## Source of truth

`djangocfg` is the source of truth for this module. After every change:

```bash
rsync -av --delete --exclude='__pycache__' \
  src/django_cfg/modules/django_generator/openapi/tools/openapi_processor/ \
  /path/to/cmdop_server/opensource/src/devtools/generator/tools/openapi_processor/
```
