"""Runtime zod-validation block for generated SWR hooks.

WHY:
   The TS types from Hey API say "this endpoint returns ``Array<X>``"
   but DRF often wraps responses in ``{count, results, ...}`` — the
   types lie. Even when the wrapper is consistent, drf-spectacular
   sometimes hashes serialiser fields differently from one regen to
   the next. Either way the runtime can drift from the schema, and
   then `data.slice()` blows up in production with no breadcrumbs.

   Validating each response against the generated zod schema catches
   that drift the moment it happens, points at the exact field that
   doesn't match, and dispatches a `zod-validation-error` browser
   event the host can hook into for global telemetry.

WHEN VALIDATION RUNS:
   * Operation has a ``response_schema_ref`` (i.e. drf-spectacular
     produced a named component for the 200 response).
   * The schema file is generated under
     ``../schemas/<Ref>.ts`` exporting ``<Ref>Schema``.

   When the response is inline (no $ref) we **skip** validation and
   fall through with an unsafe cast — there's no schema to validate
   against. That keeps the change additive: today's broken
   endpoints are no worse than before, and once the backend exposes
   a named schema validation kicks in automatically.

OUTPUT:
   ``imports`` is appended to the file's import block (empty: the schema
                is loaded lazily inside ``body``).
   ``body``     is the inside of the SWR fetcher; it starts the background
                validation and returns the raw payload.

The fetcher template substitutes both with no other knowledge of the
schema layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..ir import IROperation


@dataclass(frozen=True)
class ValidationBlock:
    imports: str
    body: str


def runtime_validation_block(op: IROperation) -> ValidationBlock:
    """Render the runtime-validation slice for one operation.

    Returns a no-op block (just ``return data;``) when the schema
    isn't a named component — there's nothing to validate against.
    """
    ref = op.response_schema_ref
    if not ref:
        return ValidationBlock(
            imports="",
            body="      return data;",
        )

    schema_const = f"{ref}Schema"
    op_id = op.operation_id
    method = op.method.upper()
    path = op.path

    # Validation is diagnostics, so it runs OFF the data path: the schema
    # module is imported after the response arrives and the hook returns the
    # raw payload at once. A static import put zod (~100 KB gz) and every
    # schema into the initial bundle of each app that mounts one hook, for a
    # check that never changes what the caller gets. On drift: log, dispatch
    # `zod-validation-error`, keep the UI running (the old throw killed the
    # page over one field).
    #
    # Returning the raw payload drops zod `.default()` fill-ins. Audited
    # 2026-10-18: every defaulted response field (`requires_2fa`,
    # `is_new_user`, `unanswered_messages_count`, `total`) is read by
    # truthiness or not at all, and DRF emits declared fields anyway.
    return ValidationBlock(
        imports="",
        body=f"""      void import("../schemas/{ref}")
        .then(({{ {schema_const} }}) => {{
          const parsed = {schema_const}.safeParse(data);
          if (parsed.success) return;
          // Log first so the failure is always visible, even if the
          // event handler swallows it.
          console.warn(
            "[zod] response did not match schema",
            {{
              operation: "{op_id}",
              method: "{method}",
              path: "{path}",
              issues: parsed.error.issues,
              data,
            }},
          );
          if (typeof window !== "undefined") {{
            try {{
              window.dispatchEvent(
                new CustomEvent("zod-validation-error", {{
                  detail: {{
                    operation: "{op_id}",
                    method: "{method}",
                    path: "{path}",
                    issues: parsed.error.issues,
                    data,
                    timestamp: new Date(),
                  }},
                  bubbles: true,
                  cancelable: false,
                }}),
              );
            }} catch {{
              // Event dispatch is best-effort.
            }}
          }}
        }})
        .catch(() => {{
          // A schema chunk that fails to load is not the caller's problem.
        }});
      return data;""",
    )
