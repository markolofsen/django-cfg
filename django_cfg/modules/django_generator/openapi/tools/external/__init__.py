"""Subprocess wrappers around external OpenAPI/proto codegen CLIs.

Each module exposes:
  - check() -> str | None : None if available, install hint otherwise
  - generate(spec_path|proto_dir, out_dir, **opts) -> Result dataclass
"""

from . import (
    buf_proto,
    grpc_python,
    hey_api,
    ogen,
    openapi_python_client,
    swift_openapi,
)

__all__ = [
    "buf_proto",
    "grpc_python",
    "hey_api",
    "ogen",
    "openapi_python_client",
    "swift_openapi",
]
