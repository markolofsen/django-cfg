# OpenAPI SDK Generator

Multi-language SDK codegen pipeline driven by a single OpenAPI spec rendered
by drf-spectacular. Supports TypeScript, Python, Go, Swift, and Protobuf
targets in one `make gen` run.

---

## Architecture

```
openapi/
  service.py              — DjangoOpenAPI entry point, wires config → pipeline
  pipeline/
    spec_loader.py        — renders spec via drf-spectacular
    slicer.py             — slices spec by tag set per group
    cache.py              — two-layer content-addressed cache (spec + per-target)
    config.py             — OpenAPIConfig, GenerationTarget, RunReport dataclasses
    postprocess.py        — tag normalisation, nullable 3.1→3.0 fixes
    runner/
      orchestrator.py     — parallel fan-out (ThreadPoolExecutor), timing, cache
      dispatch.py         — per-target tool dispatch + run_single cache loop
      cache_keys.py       — fingerprint helpers (SHA-256)
      paths.py            — project root detection, publish, mirror-to-tmp
      progress.py         — per-target timing output to stderr
      ts_wrapper.py       — TS wrapper layer + stale-root cleanup
  groups/
    resolver.py           — resolves tag sets from OpenAPIGroupConfig + apps
    detector.py           — detects groups from URL patterns
    discovery.py          — app-level tag discovery
    manager.py            — group lifecycle
  spectacular/
    enum_naming.py        — collision detector + warning reporter
    enum_overrides_service.py — matches TextChoices classes to collisions
    schema.py             — custom AutoSchema (two-tag scheme)
    async_detection.py    — async view detection
  tools/
    external/
      hey_api.py          — @hey-api/openapi-ts (TypeScript)
      ogen.py             — ogen (Go), auto-generates .ogen.yml
      openapi_python_client.py — openapi-python-client (Python)
      swift_openapi.py    — swift-openapi-generator (Swift)
      buf_proto.py        — buf (Protobuf)
      grpc_python.py      — grpc_python (Python gRPC stubs)
    ts_extras/
      schemas/            — Zod schema generator (OpenAPI → z.object/z.record/…)
      hooks/              — SWR query + mutation hooks generator
      events/             — WebSocket/SSE events.ts generator
      wrapper/            — api.ts / index.ts wrapper layer
```

---

## Two-Layer Cache

Generation is expensive (drf-spectacular + external tool boot). Two caches
short-circuit the work:

| Layer | Key | Stored in |
|---|---|---|
| **Spec cache** | SHA-256 of mtime+size of all serializer/views/urls files | `<cache_dir>/spec/` |
| **Target cache** | SHA-256 of sliced spec + tool + options + target signature | `<cache_dir>/runs/<target>/` |

On a warm run (nothing changed) both layers hit and the full pipeline takes
under 5 seconds regardless of target count.

### Disabling the cache

```bash
# Skip both layers — forces a full re-render + tool run.
DJANGO_CFG_GEN_NO_CACHE=1 make gen
```

Use this when you change generator Python code (the cache fingerprint covers
the spec and tool config, not the generator source itself).

---

## Parallelism

Targets run in a `ThreadPoolExecutor`. External tools (`ogen`, `hey-api`, etc.)
are subprocess calls that release the GIL, so N targets run in ~N× wallclock
speedup.

```bash
# Override worker count (default: min(8, cpu_count, target_count))
DJANGO_CFG_GEN_PARALLELISM=1 make gen   # serial — easier to debug
DJANGO_CFG_GEN_PARALLELISM=4 make gen   # force 4 workers
```

---

## Console Output

Per-target timing is printed to stderr so stdout stays clean for tooling:

```
  spec         0.24s   (render)
  ✓ typescript-web-0              12.34s
  ✓ python-sdk-1                   2.75s   (cached)
  ✗ go-cli-2                       1.10s   ToolExecutionError: …
  total 14.98s · slowest typescript-web-0 12.34s · 1/3 cached
```

Silence all output:

```bash
DJANGO_CFG_GEN_QUIET=1 make gen
```

Disable ANSI colours:

```bash
NO_COLOR=1 make gen
```

---

## Enum Collision Handling

drf-spectacular appends a hex hash to enum names when two serializers expose
the same field name with different choices (e.g. `Status58bEnum`). This makes
generated SDK types unstable across regenerations.

**Detect collisions:**

```bash
python manage.py suggest_enum_overrides
```

Output is a ready-to-paste `ENUM_NAME_OVERRIDES` dict. Add it to your config:

```python
from django_cfg.models.api.drf import SpectacularConfig

config = DjangoConfig(
    spectacular=SpectacularConfig(
        enum_name_overrides={
            'WorkspaceInvitationStatusEnum': 'apps.workspaces.models.WorkspaceInvitation.Status',
            'WorkspaceMemberRoleEnum': 'apps.workspaces.models.WorkspaceMember.Role',
        },
    ),
)
```

> **Note:** drf-spectacular's format is **inverted** — KEY is the desired enum
> name, VALUE is the dotted path to the `TextChoices` subclass.

**Collision policy** (controls warning vs hard error in CI):

```bash
DJANGO_CFG_ENUM_COLLISION_POLICY=error make gen   # block CI on collisions
DJANGO_CFG_ENUM_COLLISION_POLICY=warn  make gen   # default — warn only
DJANGO_CFG_ENUM_COLLISION_POLICY=ignore make gen  # silence
```

---

## Zod Schema Generation (`ts_extras/schemas/`)

The Zod converter (`converter.py`) maps OpenAPI types to Zod v4 expressions:

| OpenAPI | Zod |
|---|---|
| `type: string` | `z.string()` |
| `type: integer` | `z.number().int()` |
| `type: boolean` | `z.boolean()` |
| `type: array, items: T` | `z.array(T)` |
| `type: object, properties: {…}` | `z.object({…})` |
| `additionalProperties: {type: X}` | `z.record(z.string(), X)` |
| `additionalProperties: {} / true` | `z.record(z.string(), z.unknown())` |
| `additionalProperties: false` | `z.object({})` |
| `anyOf: [T, null]` | `T.nullable()` |
| `$ref: #/components/schemas/Foo` | `FooSchema` |
| no type | `z.unknown()` |

> Zod v4 requires two arguments for `z.record(keySchema, valueSchema)`.
> The generator always emits `z.record(z.string(), …)`.

---

## Adding a New Tool

1. Add a wrapper in `tools/external/<tool>.py` — expose a `generate(spec_path, out_dir, **opts)` function.
2. Add the tool name to `GenerationTarget.tool` literal in `pipeline/config.py`.
3. Add a dispatch branch in `pipeline/runner/dispatch.py` → `_dispatch_tool()`.
4. Add a target in your project's `generation.py`.
