# django_generator

Clean-room rewrite of `django_client/` modeled on the FastAPI-side cmdop
generator. Thin orchestrator over external CLIs (ogen, Orval,
openapi-python-client, swift-openapi-generator, buf). TypeScript targets are
generated from OpenAPI by the pinned Orval tool into a React Query/Zod/MSW
client; Python/Go/Swift targets keep their own external generators.

## Pipeline

```
drf-spectacular → spec_loader → postprocess → resolve_tags → slicer
                                                                │
                                       ┌────────────────────────┘
                                       ▼
                       external CLI (ogen / Orval / openapi-python-client / …)
                                       │
                                       ▼
                                  <Target.path>/
                                       │
                                       ▼
                          .tmp/generated/<name>/  (mirror, dev only)
```

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
brew install bufbuild/buf/buf
brew install apple/tap/swift-openapi-generator
brew install swift-protobuf grpc-swift   # for proto-Swift targets
# Orval is installed and pinned in the frontend workspace (Node 22.18+ required)
```

`python manage.py gen --check` probes every CLI and prints install hints
for any that are missing.

## Test loop

`make gen` in `solution/django/` is the integration acceptance gate.

## API base URL strategy

Generated `helpers/auth.ts` resolves `baseUrl` from `NEXT_PUBLIC_API_URL` on
both server and browser — requests go directly to Django.

### Why no same-origin fallback in the generator

Earlier versions returned `''` in the browser so Next.js rewrites could
intercept requests and proxy them server-side (useful when an API key must
never reach the browser). That logic was removed from the generator because:

1. It is **project-specific**, not a universal pattern.
2. Most apps (`my`, `crm`) talk to Django directly — no proxy needed.

### How catalog-api handles the proxy exception

`@carapis/catalog-api` is the one package that routes browser requests through
a Next.js Route Handler (`/api/apix/[...path]/route.ts`) so the API key is
injected server-side and never exposed in the browser bundle.

This is achieved in `packages/catalog-api/src/client/index.ts` (a
hand-maintained file, never overwritten by `make gen`):

```ts
// Browser → same-origin so Route Handler proxies + injects API key
if (typeof window !== 'undefined') {
  auth.setBaseUrl('');
}
```

Server-side `defaultBaseUrl()` returns `NEXT_PUBLIC_API_URL` as usual.

### Rule

Do **not** add `isBrowser → ''` back to the generator template.
If a new package needs proxy behaviour, override `auth.setBaseUrl('')` in its
own hand-maintained entry point.
