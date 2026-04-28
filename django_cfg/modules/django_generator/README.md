# django_generator

Clean-room rewrite of `django_client/` modeled on the FastAPI-side cmdop
generator. Thin orchestrator over external CLIs (ogen, Hey API,
openapi-python-client, swift-openapi-generator, buf) plus a `ts_extras/`
layer that adds zod schemas, SWR hooks, and an `events.ts` bridge on top
of Hey API output.

## Pipeline

```
drf-spectacular → spec_loader → postprocess → resolve_tags → slicer
                                                                │
                                       ┌────────────────────────┘
                                       ▼
                       external CLI (ogen / hey-api / openapi-python-client / …)
                                       │
                                  (TS only)
                                       ▼
                       ts_extras (zod / SWR hooks / events.ts)
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
# Hey API runs via npx — no install step (Node 18+ required)
```

`python manage.py gen --check` probes every CLI and prints install hints
for any that are missing.

## Test loop

`make gen` in `solution/django/` is the integration acceptance gate.

## Status

See [@dev/STATUS.md](@dev/STATUS.md). Phases 1–5 implemented; Phase 6
(cutover from `django_client/` and deletion of legacy module) is gated
on user decision.
