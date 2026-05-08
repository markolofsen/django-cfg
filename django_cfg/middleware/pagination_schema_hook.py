"""drf-spectacular post-processing hook for paginated list endpoints.

WHY:
   ``DefaultPagination.get_paginated_response_schema`` returns the
   wrapper shape inline. drf-spectacular then embeds that block
   verbatim into every list endpoint's 200 response. Two follow-on
   problems:

   1. The TS codegen (``ts_extras``) refuses to generate zod schemas
      for inline responses — so paginated endpoints lose runtime
      validation, and the frontend trusts ``Array<X>`` types that
      lie about the wire shape.
   2. ``count``, ``pages``, etc. are duplicated across hundreds of
      operations in the spec, bloating the OpenAPI document.

WHAT THIS HOOK DOES:
   Walks every operation response with HTTP code in {200, 201}, looks
   for an inline schema that matches the *exact* shape produced by
   ``DefaultPagination`` (page-based pagination with the extra
   ``has_next`` / ``has_previous`` / ``next_page`` / ``previous_page``
   fields — that mix is unique to django-cfg, so we don't collide
   with stock DRF paginators).

   When the inner ``results.items`` is a ``$ref`` to a named
   component ``X``, the hook:

     * extracts the wrapper into ``components.schemas`` under
       ``Paginated{X}List`` (created once per inner type),
     * replaces the inline schema with ``{"$ref": …}``.

   Idempotent: re-running on an already-promoted spec is a no-op.

   When ``results.items`` is itself inline (no ``$ref``) we leave the
   wrapper inline — there's nothing reusable to point at. A debug log
   line names the offending operation so the developer can promote
   the inner serializer to a registered component if they want zod.

WHAT THIS HOOK DOES NOT DO:
   It does not police bare-array responses. Plenty of list-style
   endpoints intentionally return a flat ``Array<X>`` — autocomplete
   typeaheads (capped server-side), enum lookups, sidebar trees that
   need the whole structure at once. The author signals that intent
   with ``pagination_class = None`` or by using ``APIView`` with
   ``many=True``. We trust that signal. The runtime zod check in the
   generated SWR hooks (separate concern) catches schema-vs-wire
   drift if someone later adds a wrapper without updating the spec.

USAGE:
   Wired into the default ``postprocessing_hooks`` list of
   ``django_cfg.models.api.drf.SpectacularConfig``. Manual import:

       SPECTACULAR_SETTINGS = {
           "POSTPROCESSING_HOOKS": [
               "django_cfg.middleware.pagination_schema_hook.extract_paginated_components",
           ],
       }
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Fields produced by ``DefaultPagination.get_paginated_response_schema``.
# We require at least these to declare a wrapper "ours" — the trio
# ``page`` / ``pages`` / ``has_next`` doesn't appear in stock DRF's
# pagination shapes, so this matcher is precise without hard-coding
# the full property list (which might evolve).
_REQUIRED_FIELDS = frozenset({"count", "page", "pages", "has_next", "results"})

# 2xx response codes that may carry a paginated body.
_LIST_CODES = ("200", "201")


def extract_paginated_components(
    result: dict[str, Any],
    generator: Any | None = None,
    request: Any | None = None,
    public: Any | None = None,
    **_: Any,
) -> dict[str, Any]:
    """drf-spectacular post-processing hook entry point.

    The signature matches ``drf_spectacular`` conventions — ``result``
    is the in-progress OpenAPI dict, the rest are unused but kept so
    the framework can pass them positionally.

    Returns the (mutated) ``result``. Mutation in place is the
    convention for these hooks.
    """
    if not isinstance(result, dict):
        return result

    paths = result.get("paths") or {}
    components = result.setdefault("components", {})
    schemas = components.setdefault("schemas", {})

    promoted = 0
    skipped_inline_inner = 0

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            responses = operation.get("responses") or {}
            if not isinstance(responses, dict):
                continue
            for code in _LIST_CODES:
                response = responses.get(code)
                if not isinstance(response, dict):
                    continue
                content = response.get("content") or {}
                json_part = content.get("application/json") or {}
                schema = json_part.get("schema")
                if not isinstance(schema, dict):
                    continue

                if "$ref" in schema:
                    # Already named — could be from a previous run or
                    # an explicitly-registered serializer. Nothing to do.
                    continue

                if not _matches_default_paginator(schema):
                    continue

                inner_ref = _extract_inner_ref(schema)
                if inner_ref is None:
                    skipped_inline_inner += 1
                    op_id = operation.get("operationId", f"{method.upper()} {path}")
                    logger.debug(
                        "pagination_schema_hook: %s has inline paginated wrapper "
                        "but inner items are also inline (no $ref). Promote the "
                        "inner serializer to a named component to enable zod "
                        "validation downstream.",
                        op_id,
                    )
                    continue

                component_name = f"Paginated{inner_ref}List"
                if component_name not in schemas:
                    schemas[component_name] = _build_named_wrapper(schema, inner_ref)

                json_part["schema"] = {
                    "$ref": f"#/components/schemas/{component_name}"
                }
                promoted += 1

    if promoted or skipped_inline_inner:
        logger.info(
            "pagination_schema_hook: promoted=%d skipped_inline_inner=%d",
            promoted,
            skipped_inline_inner,
        )
    return result


# ── Internals ────────────────────────────────────────────────────────


def _matches_default_paginator(schema: dict[str, Any]) -> bool:
    """True when ``schema`` looks like our ``DefaultPagination`` wrapper.

    We don't insist on every property being present (drf-spectacular
    sometimes prunes unused ones); just on the characteristic mix.
    """
    if schema.get("type") != "object":
        return False
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return False
    if not _REQUIRED_FIELDS.issubset(properties.keys()):
        return False
    results = properties.get("results")
    if not isinstance(results, dict):
        return False
    if results.get("type") != "array":
        return False
    return True


def _extract_inner_ref(schema: dict[str, Any]) -> str | None:
    """Return the inner component name when ``results.items`` is a $ref.

    Drilldown is intentionally narrow — only the canonical
    ``{ "$ref": "#/components/schemas/X" }`` form. Anything more
    exotic (allOf, oneOf, inline object) is treated as inline and
    triggers the skip path above.
    """
    items = (schema.get("properties") or {}).get("results", {}).get("items")
    if not isinstance(items, dict):
        return None
    ref = items.get("$ref")
    if not isinstance(ref, str):
        return None
    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        return None
    name = ref[len(prefix):]
    return name or None


def _build_named_wrapper(inline_schema: dict[str, Any], inner_ref: str) -> dict[str, Any]:
    """Clone the inline wrapper for storage as a named component.

    We deep-copy the property dict to insulate the registry from
    further mutation and tag the schema with a description that names
    the inner type — useful when reading the OpenAPI document.
    """
    import copy

    cloned = copy.deepcopy(inline_schema)
    cloned.setdefault(
        "description",
        f"Paginated list of {inner_ref} items (django-cfg DefaultPagination).",
    )
    return cloned
