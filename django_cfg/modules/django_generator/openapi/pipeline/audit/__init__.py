"""Spec audit checks.

Lints the (post-loaded, pre-slice) OpenAPI spec for known patterns
that crash downstream client generators. Each check is a pure
function that takes the spec dict and returns a list of human-readable
warnings — never mutates and never raises.
"""

from .requestbody import audit_requestbody_content_types

__all__ = ["audit_requestbody_content_types"]
