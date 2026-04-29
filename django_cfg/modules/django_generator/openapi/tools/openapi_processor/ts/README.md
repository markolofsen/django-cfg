# ts_extras

**Post-processor for Hey API output.** Takes a sliced OpenAPI spec and emits
everything that `@hey-api/openapi-ts` deliberately does not: Zod schemas, SWR
hooks, a Centrifugo events bridge, and typed `class API` wrappers with JWT
interceptors and runtime validation.

---

## Why it exists

`@hey-api/openapi-ts` is great at generating a raw SDK — types, a fetch client,
class-per-tag methods. It stops there by design. Real app code needs more:

- **Runtime validation** — a 200 response is not trustworthy until Zod parses it.
- **SWR hooks** — `useFleetsList()` / `useFleetsCreate()` instead of
  calling the SDK directly in every component.
- **Realtime events bridge** — a typed `events.ts` that maps Centrifugo
  publication channels onto TS types so the frontend never hardcodes a
  channel string.
- **`class API` per group** — a single entry-point per tag-group that owns
  JWT storage, wires the Authorization header interceptor, and exposes only
  the SDK classes that belong to that group.

These are generated once, kept in sync with the spec on every `make gen`, and
never hand-edited.

---

## Relationship to Hey API

```
OpenAPI spec
    │
    ▼
@hey-api/openapi-ts          ← step 1 (external tool)
    │   sdk.gen.ts            (class Fleets, class Auth, …)
    │   types.gen.ts          (all TS types)
    │   client/  core/
    │
    ▼
ts_extras                    ← step 2 (this module, post-processor)
    │   _fleets/schemas/      (Zod schemas for Fleets responses)
    │   _fleets/hooks/        (useFleetsListQuery, …)
    │   _fleets/events.ts     (channel → type map)
    │   _fleets/api.ts        (class API — JWT + interceptor + Zod routes)
    │   _fleets/index.ts
    │   helpers/              (StorageAdapter, APIError, APILogger, …)
    │   index.ts              (top-level barrel)
```

The two steps share no state at runtime. Hey API runs first (clears and
writes `target/`), ts_extras runs second and writes only into `_<group>/`
subdirs and `helpers/` — it never touches `sdk.gen.ts` or `types.gen.ts`.

---

## Architecture

```
ts_extras/
  ir.py             — minimal IR over a (sliced) OpenAPI 3.1 spec
  naming.py         — operation-id → hook name / schema name conventions
  tool.py           — entry point: build_ir → schemas → hooks → events
  schemas/          — OpenAPI → Zod source generator
  hooks/            — IR → SWR query + mutation hook generator
  events/           — emits events.ts (Centrifugo channel bridge)
  wrapper/          — reads sdk.gen.ts → emits class API + helpers
```

### IR (intermediate representation)

`ir.py` walks the raw OpenAPI dict and produces two flat lists:

- `IRSchema` — every entry from `components.schemas`
- `IROperation` — every HTTP operation (method, path, primary tag, refs to
  request/response schemas)

Nothing else is parsed. The IR is intentionally thin — generators read
`IRSchema.raw` directly when they need full schema detail.

### schemas/

Converts `components.schemas` to individual `<SchemaName>.ts` files, each
exporting one `z.object(…)` (or `z.string()`, `z.enum()`, etc.). Handles
`$ref` resolution, `allOf` / `oneOf`, nullable variants, and enum modes.
Writes `schemas/index.ts` barrel.

### hooks/

Reads `IROperation` list and emits one file per hook, **flat** inside
`hooks/` (no per-tag subdirectory).

Hook kinds:

- **Query hooks** (`GET` / `HEAD`) — `use<OperationId>(args?, config?)`
  wraps `useSWR`. Generated for **every** GET, including paginated ones.
  Returns the page object as-is (`{ results, count, has_next, ... }`)
  so app code reads `data?.results` and `data?.count` directly. This is
  the default for tables and any URL-driven pagination.
- **Infinite-scroll hooks** (`GET` with `Paginated*` response, **additional**) —
  `use<OperationId>Infinite(args?, config?)` wraps `useSWRInfinite`.
  Strips `page` from the query slot and controls it internally; exposes
  `flatData` (concatenated `results` across loaded pages), `count`,
  `has_next`, `has_previous`, and `loadMore()`. Reach for this only on
  feeds/chats — not for page-numbered tables.
- **Mutation hooks** (`POST` / `PUT` / `PATCH` / `DELETE`) —
  `use<OperationId>(config?)` wraps `useSWRMutation`, returns
  `{ trigger, isMutating, error }`. Args (`{ path?, query?, body? }`)
  are passed to `trigger(args)` at call time.

For paginated endpoints **both** the page-based and the `Infinite`
variant are emitted side-by-side (e.g., `useApiKeysList` +
`useApiKeysListInfinite`). The `Infinite` SWR key is suffixed with
`_infinite` to avoid colliding with the page-based hook's cache.

All hooks import from `../../sdk.gen` and `../../types.gen` (two levels up
from `_<group>/hooks/` to `generated/`). A single `hooks/index.ts` barrel
re-exports everything.

Param typing is delegated to Hey API's `XData` types via
`Omit<XData, "url" | "body">` — the generator never re-emits inline TS
property declarations, so no drift between SDK and hook signatures.

### events/

Emits `events.ts` — a typed map of Centrifugo channel patterns to their
publication payload types. Downstream code subscribes with `onEvent('fleets.*',
handler)` and gets typed payloads automatically.

### wrapper/

Post-processes the **already-written** per-group output:

1. Reads the root `sdk.gen.ts` produced by Hey API.
2. Discovers which SDK classes belong to each `_<group>/` dir by name matching.
3. For each group, emits:
   - `api.ts` — `class API` that mounts SDK classes as readonly props,
     manages JWT via a pluggable `StorageAdapter`, wires the Hey API
     request interceptor for `Authorization: Bearer`, and provides
     per-route Zod validation via `.routes.json` written by the schemas
     generator.
   - `index.ts` — barrel re-exporting `API` + `StorageAdapter` variants +
     `APIError` + `APILogger` + validation events helpers.
4. Writes shared `helpers/` (storage adapters, error types, logger, Zod
   event dispatcher) once per target.
5. Writes a top-level `index.ts` with Next.js-safe singleton exports.

---

## Usage as a post-processor

`ts_extras` is designed to be backend-agnostic. It only needs a valid
(sliced) OpenAPI 3.1 spec. The same module is used unchanged for both the
Django backend and the FastAPI backend — copy it verbatim, point it at a
different spec, get identical output structure.

### Standalone invocation

```python
from devtools.generator.tools.openapi_processor.ts.tool import generate

generate(
    spec_path=Path("openapi.json"),
    out_dir=Path("generated/_fleets"),
    extras=["zod", "hooks", "events"],
)
```

### As a wrapper pass (after Hey API)

```python
from devtools.generator.tools.openapi_processor.ts.wrapper.generator import generate as generate_wrapper

generate_wrapper(target_dir=Path("generated"))
```

### Selecting sub-generators

`extras` is a list — any subset of `["zod", "hooks", "events"]`. Omit any
you don't need. The wrapper pass runs separately and always operates on the
full target dir.

---

## Output layout (per group)

```
generated/
  _fleets/
    schemas/
      FleetList.ts
      FleetCreate.ts
      …
      index.ts
    hooks/                              ← flat — one file per hook
      useFleetsFleetsList.ts            ← query     (useSWR, page-based)
      useFleetsFleetsListInfinite.ts    ← infinite  (useSWRInfinite, `_infinite` key)
      useFleetsFleetsMeRetrieve.ts      ← query     (useSWR, single resource)
      useFleetsCreate.ts                ← mutation  (useSWRMutation)
      …
      index.ts
    events.ts
    api.ts          ← class API (wrapper)
    index.ts        ← barrel
  helpers/
    storage.ts
    errors.ts
    logger.ts
    validation-events.ts
    index.ts
  index.ts          ← top-level barrel
  sdk.gen.ts        ← written by Hey API, not touched here
  types.gen.ts      ← written by Hey API, not touched here
```

---

## Portability

- **Zero external Python deps** beyond the standard library — pure string
  generation, no Jinja2, no Mako.
- **No project-specific imports** — the module does not reference Django,
  FastAPI, or any other service. Drop it into any generator package.
- **Idempotent** — re-running produces identical output given the same spec.
  Safe to commit generated files and diff them in CI.
