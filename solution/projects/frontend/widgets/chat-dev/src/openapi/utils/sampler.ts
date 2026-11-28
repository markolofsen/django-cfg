/**
 * JSON Schema → example JSON.
 *
 * Thin wrapper over ``openapi-sampler`` (by Redocly — same library Redoc
 * uses internally). Picks deterministic, realistic values from a
 * dereferenced schema: honours ``const`` / ``examples`` / ``enum`` /
 * ``default``, unpacks ``allOf`` / ``oneOf`` / ``anyOf``, respects
 * string ``format`` (email/uuid/date-time/…).
 *
 * Replaces the previous hand-rolled ``exampleFromSchema`` — stricter on
 * spec semantics and cheaper to maintain.
 */

import consola from 'consola';
import { sample as openapiSample } from 'openapi-sampler';

type JsonSchemaLike = Record<string, unknown>;

export interface SampleOptions {
    /** Skip properties marked ``readOnly`` — useful when the body will
     *  be sent in a request (request body editor). Default ``false``. */
    skipReadOnly?: boolean;
    /** Skip properties marked ``writeOnly`` — useful when rendering a
     *  response body (passwords etc. must not leak). Default ``false``. */
    skipWriteOnly?: boolean;
    /** Skip non-required properties. Rarely useful for a viewer — we
     *  want to show the full shape. Default ``false``. */
    skipNonRequired?: boolean;
}

/** Sample a JSON schema into a plain value. Returns ``null`` on failure
 *  (malformed schema, circular refs the sampler can't unwind) so the
 *  caller can show "no example" instead of crashing the page.
 *
 *  ``spec`` must be the root OpenAPI document whenever ``schema`` may
 *  contain ``$ref`` nodes — ``openapi-sampler`` walks the tree and
 *  resolves refs against it. Our own ``dereferenceSchema`` only inlines
 *  refs up to a depth limit; anything deeper comes through here as a
 *  live ``$ref`` and the sampler throws if ``spec`` is missing. */
export function sampleSchema(
    schema: JsonSchemaLike | undefined,
    options: SampleOptions = {},
    spec?: unknown,
): unknown {
    if (!schema) return null;
    try {
        return openapiSample(schema as never, options, spec as never);
    } catch (err) {
        // Sampler failures used to be silent, which meant "no example"
        // in the UI looked like a missing spec entry. Log so we can see
        // the real cause in dev (circular refs, missing type, etc.).
        consola.warn('[OpenapiViewer] sampleSchema failed:', err, { schema });
        return null;
    }
}

/** Same as ``sampleSchema`` but returns a pre-stringified JSON payload
 *  ready to drop into a textarea / code block. Returns ``undefined``
 *  when sampling fails so the UI can conditionally hide the example. */
export function sampleSchemaJson(
    schema: JsonSchemaLike | undefined,
    options: SampleOptions = {},
    spec?: unknown,
): string | undefined {
    const value = sampleSchema(schema, options, spec);
    if (value === null || value === undefined) return undefined;
    try {
        return JSON.stringify(value, null, 2);
    } catch {
        return undefined;
    }
}
