"""Python post-processor for openapi-python-client output.

Applies fixes for known upstream bugs and conventions. Currently:

- ``unset_import``: when a generated file uses ``| Unset = UNSET`` in a
  function signature but only imports ``UNSET`` (not ``Unset``), inject
  ``Unset`` into the import line. This is a long-standing issue in
  openapi-python-client — the type annotation references ``Unset`` but
  the import shim only carries ``UNSET, Response``.
"""

from .tool import PythonExtrasResult, generate

__all__ = ["PythonExtrasResult", "generate"]
