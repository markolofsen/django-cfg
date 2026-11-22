"""Mapping from operationId to Hey API sdk function/type names.

Hey API generates names with toCase() from @hey-api/openapi-ts/shared.
Key behaviour: digit-sequences followed by a letter/digit are uppercased
in camelCase/PascalCase output, so "m3u8" → "M3U8" (not "M3u8").

operationId may contain a dot that separates the *class* part from the
*method* part, e.g. "terminal_hls_master.m3u8_retrieve":
    class  = terminal_hls_master → TerminalHlsMaster
    method = m3u8_retrieve       → m3U8Retrieve (camelCase)
    types  = TerminalHlsMasterM3U8Retrieve{Data,Responses}

These are the names ts_extras hooks import from the Hey API output. If
Hey API ever changes the convention, this is the only file to update.
"""

from __future__ import annotations

import re

from ..ir import IROperation

_SEPARATORS = re.compile(r"[_.\-\s]+")

# Mirrors Hey API's numbersAndIdentifierRegExp: digit-sequence followed by
# a word character (letter, digit, or underscore) that is NOT followed by a
# separator character.  We uppercase the whole match to replicate toCase().
_NUMS_AND_ID = re.compile(r"\d+[a-zA-Z\d]")


def _hey_api_camel(s: str) -> str:
    """Convert a snake/dot/kebab string to camelCase the way Hey API does.

    Differences from plain .capitalize():
      - digit+letter sequences are fully uppercased: m3u8 → m3U8
        (Hey API's numbersAndIdentifierRegExp behaviour)
    """
    parts = [p for p in _SEPARATORS.split(s.strip()) if p]
    if not parts:
        return ""

    def _part_to_upper(part: str) -> str:
        """Capitalise a word, uppercasing any digit-adjacent letters."""
        if not part:
            return ""
        # first upper the initial letter
        result = part[0].upper() + part[1:]
        # then uppercase digit-followed-by-letter sequences within the part
        result = _NUMS_AND_ID.sub(lambda m: m.group(0).upper(), result)
        return result

    head = parts[0].lower()
    # Apply digit-adjacent uppercasing to the head too (e.g. "m3u8" → "m3U8")
    head = _NUMS_AND_ID.sub(lambda m: m.group(0).upper(), head)

    tail = "".join(_part_to_upper(p) for p in parts[1:])
    return head + tail


def _hey_api_pascal(s: str) -> str:
    """Convert to PascalCase the way Hey API does (uppercase digit+letter)."""
    parts = [p for p in _SEPARATORS.split(s.strip()) if p]
    if not parts:
        return ""

    def _part_to_upper(part: str) -> str:
        if not part:
            return ""
        result = part[0].upper() + part[1:]
        result = _NUMS_AND_ID.sub(lambda m: m.group(0).upper(), result)
        return result

    return "".join(_part_to_upper(p) for p in parts)


def _split_operation_id(operation_id: str) -> tuple[str, str]:
    """Split operationId on the first dot into (class_part, method_part).

    If there is no dot the class_part equals the full operationId and
    method_part is empty (indicating a flat operationId).
    """
    if "." in operation_id:
        cls_part, method_part = operation_id.split(".", 1)
        return cls_part, method_part
    return operation_id, ""


def sdk_fn_name(op: IROperation) -> str:
    """Return the Hey API SDK method name for this operation.

    For dotted operationIds (e.g. terminal_hls_master.m3u8_retrieve) Hey API
    generates the method on the *sub-class* (TerminalHlsMaster), so we only
    camelCase the post-dot part: m3u8_retrieve → m3U8Retrieve.

    For flat operationIds the full name is camelCased as one token.
    """
    cls_part, method_part = _split_operation_id(op.operation_id)
    if method_part:
        return _hey_api_camel(method_part)
    return _hey_api_camel(cls_part)


def sdk_class_name(op: IROperation) -> str:
    """Return the Hey API SDK class to call on in the hook.

    For dotted operationIds the SDK class is derived from the pre-dot part
    (e.g. terminal_hls_master → TerminalHlsMaster), *not* from the tag.
    For flat operationIds the tag-based byTags class is used.
    """
    cls_part, method_part = _split_operation_id(op.operation_id)
    if method_part:
        return _hey_api_pascal(cls_part)
    # Flat operationId — use tag (normalized to PascalCase) for byTags class.
    return _hey_api_pascal(op.tag) if op.tag else "Api"


def sdk_type_names(op: IROperation) -> tuple[str, str]:
    """Return (DataType, ResponsesType) names exported by Hey API."""
    pascal = _hey_api_pascal(op.operation_id)
    return f"{pascal}Data", f"{pascal}Responses"
