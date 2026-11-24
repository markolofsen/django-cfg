"""Subprocess wrappers around external OpenAPI/proto codegen CLIs.

Each module exposes:
  - check() -> str | None : None if available, install hint otherwise
  - generate(spec_path|proto_dir, out_dir, **opts) -> Result dataclass

``tsc`` is the exception: it generates nothing. It type-checks a generated
TypeScript tree (``typecheck``) for the gate in ``pipeline/runner/typecheck.py``.
"""

from . import (
    buf_proto,
    grpc_python,
    ogen,
    openapi_python_client,
    orval,
    progenitor,
    swift_openapi,
    tsc,
)

__all__ = [
    "buf_proto",
    "grpc_python",
    "ogen",
    "openapi_python_client",
    "orval",
    "progenitor",
    "swift_openapi",
    "tsc",
]
