# OpenAPI SDK generator

The pipeline renders one drf-spectacular document, resolves each target's
groups to OpenAPI tags, slices the document, then invokes the selected
specialist generator.

TypeScript targets use the pinned Orval tool from the frontend workspace. One
target receives one union slice; Orval's `tags-split` output keeps endpoint
modules separated by OpenAPI tag while models and runtime stay shared. The
other targets use ogen, openapi-python-client, swift-openapi-generator, buf,
or grpc-python.

## Pipeline

```
drf-spectacular → validate/fail-on-warn → spec_loader → tag resolver → slicer
                                                        → external generator
                                                        ↓
                                      staging → target.path → mirror (.tmp)
```

The generator owns group selection, slicing, content-addressed cache,
staging, contract stamps, and publication. It does not duplicate the
language-specific TypeScript generator.

## Cache and verification

```bash
DJANGO_CFG_GEN_NO_CACHE=1 make gen
python manage.py gen --check
```

The cache key includes the sliced spec, tool options, target, group set, and
output path. Every generation run invalidates target fingerprints so changes
to the Python orchestration cannot silently leave stale generated output.

Before any external generator is started, `spec_loader` applies the equivalent
of `python manage.py spectacular --validate --fail-on-warn`. This prevents
Orval, openapi-python-client, ogen, or Swift from consuming an ambiguous
contract. A project that is being migrated can temporarily set
`DJANGO_CFG_GEN_ALLOW_SCHEMA_WARNINGS=1`, but that exception should be removed
after the emitted serializer/view warnings are fixed.

## Schema discipline

Every operation should have stable `operationId` and explicit OpenAPI tags.
Use named serializers for reusable request/response shapes and
`@extend_schema(request=None)` for no-body actions. The resulting schema is
the source of truth for Orval's TypeScript types, Zod schemas, React Query
operations, and MSW mocks.

The former Hey API/`ts_extras` implementation is retained only under
`django_generator/.archive/` for historical reference; it is not imported by
the active pipeline.
