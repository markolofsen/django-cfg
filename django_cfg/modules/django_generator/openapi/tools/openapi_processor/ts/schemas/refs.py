"""Collect transitive `$ref` names from a schema dict."""

from __future__ import annotations

_REF_PREFIX = "#/components/schemas/"


def collect_refs(obj: object) -> set[str]:
    """Return every `<Name>` referenced via `#/components/schemas/<Name>`."""
    refs: set[str] = set()
    _walk(obj, refs)
    return refs


def _walk(obj: object, refs: set[str]) -> None:
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith(_REF_PREFIX):
            refs.add(ref[len(_REF_PREFIX):])
        for v in obj.values():
            _walk(v, refs)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, refs)
