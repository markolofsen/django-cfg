# django_generator

Generates API clients and ORM code from a Django project. A thin orchestrator over external tools: Orval for
TypeScript, ogen for Go, progenitor for Rust, openapi-python-client for Python, swift-openapi-generator for Swift, buf and grpc-python for
protobuf. The FastAPI ORM generator is separate (`fastapi/`, `@docs/fastapi/`).

## Pipeline

```
drf-spectacular → validate (fail on warn) → normalize → per target: groups → tags → slice → stamp
    → external tool (Orval: + request flags, realtime topics, shim, cfg.ts, prettier)
    → type-check gate (TypeScript) → git guard → swap into Target.path → mirror (.tmp, dev only)
```

Step by step, with file paths: [`@docs/openapi/pipeline.md`](@docs/openapi/pipeline.md). What the TypeScript output
contains and the Target options: [`openapi/README.md`](openapi/README.md).

## Public API

```python
from django_cfg.modules.django_generator import (
    OpenAPIConfig,
    OpenAPIGroupConfig,
    DjangoOpenAPI,
    get_openapi_service,
    get_openapi_urls,
)
```

## Installation

```bash
# Python deps
pip install "django-cfg[gen]"

# External CLIs
go install github.com/ogen-go/ogen/cmd/ogen@latest
cargo install cargo-progenitor --version 0.17.0 --locked   # Rust targets (pinned)
brew install bufbuild/buf/buf
brew install apple/tap/swift-openapi-generator
brew install swift-protobuf grpc-swift   # for proto-Swift targets
# Orval is installed and pinned in the frontend workspace (Node 22.18+ required)
```

A missing CLI fails its target with the install hint. `python manage.py gen --check` (`make gen-check`) generates
nothing: it fails when a client's CFG contract differs from the installed django-cfg or the Django schema changed
since the client was generated ([@docs/openapi/pipeline.md](@docs/openapi/pipeline.md#checking-without-generating-gen---check)).

## Test loop

- `make test-fast` in `projects/django-cfg`: unit tests, the Orval golden snapshot and the generated-client smoke
  suite.
- `make gen` in `solution/django/`: the integration acceptance gate (both reference trees, type-check gate on).

Details, including `UPDATE_SNAPSHOTS=1` and `DJANGO_CFG_GEN_SKIP_TYPECHECK=1`:
[`@docs/openapi/testing.md`](@docs/openapi/testing.md).

The schema gate runs before any external generator and mirrors `manage.py spectacular --validate --fail-on-warn`.
During a controlled migration `DJANGO_CFG_GEN_ALLOW_SCHEMA_WARNINGS=1` can be used temporarily; it must not become
the normal CI or production setting.

## Developer docs

[`@docs/openapi/`](@docs/openapi/README.md): the pipeline, adding a Target option or a request flag, the tests and
gates, the Orval pin and the mechanisms we use or rejected.

## API origin

The generator writes no origin into a TypeScript tree. Where a request goes is decided at run time by the
`@djangocfg/api` runtime (`resolveApiOrigin`): an explicit `configureApi` value, a static build, a same-origin proxy
(`NEXT_PUBLIC_API_PROXY_URL=''`), or `NEXT_PUBLIC_API_URL`. A tag that must skip the proxy is the Target option
`direct_origin_tags`. The hey-api-era "API base URL strategy" (`helpers/auth.ts`, `auth.setBaseUrl('')`) is archived
in [`@docs/_archive/`](@docs/_archive/api-base-url-strategy-hey-api.md).
