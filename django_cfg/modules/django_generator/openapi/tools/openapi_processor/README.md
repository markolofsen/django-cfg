# OpenAPI post-processors

This directory contains project-specific post-processing that remains useful
for non-TypeScript generators, such as Python package fixes and Go wrappers.

TypeScript generation is owned by Orval and is configured in
`tools/external/orval.py`. The former Hey API/`ts_extras` implementation and
its tests live under `django_generator/.archive/` and are not imported by the
active pipeline.
