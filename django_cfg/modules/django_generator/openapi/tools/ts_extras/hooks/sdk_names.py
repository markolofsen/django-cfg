"""Mapping from `IROperation` to Hey API SDK class/method/type names.

With `operations.strategy: 'byTags'` Hey API emits one `export class <Tag>`
per OpenAPI tag, with operations as `public static` methods on that class:

    export class Auth {
      public static cfgAccountsLoginCreate<...>(options) { ... }
    }

So a hook needs:
    import { Auth } from "../sdk.gen";
    Auth.cfgAccountsLoginCreate(args)

Names produced here:
    sdk_class_name:  PascalCase of `op.tag` (with non-alnum stripped)
    sdk_method_name: camelCase of `op.operation_id`
    sdk_type_names:  Hey API data/responses type names

If Hey API changes the convention, this is the only file to update.
"""

from __future__ import annotations

import re

from ..ir import IROperation
from ..naming import snake_to_pascal


def sdk_class_name(op: IROperation) -> str:
    """`tag` → PascalCase class name as emitted by Hey API."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", op.tag).strip()
    if not cleaned:
        return "Default"
    return "".join(_normalize_part(p) for p in cleaned.split())


def sdk_method_name(op: IROperation) -> str:
    """`operationId` (snake_case) → camelCase method name on the SDK class."""
    parts = [p for p in op.operation_id.split("_") if p]
    if not parts:
        return "anonymous"
    head, *rest = parts
    return head.lower() + "".join(p.capitalize() for p in rest)


def sdk_type_names(op: IROperation) -> tuple[str, str]:
    """Return (DataType, ResponsesType) names exported by Hey API."""
    pascal = snake_to_pascal(op.operation_id)
    return f"{pascal}Data", f"{pascal}Responses"


def _normalize_part(part: str) -> str:
    """`TOTP` → `Totp`, `OAuth` → `OAuth`, `auth` → `Auth`.

    Hey API lowercases ALL-CAPS sequences (3+ chars) for class names — match
    that so our import resolves to the actual exported symbol.
    """
    if part.isupper() and len(part) >= 3:
        return part[0] + part[1:].lower()
    return part[0].upper() + part[1:]
