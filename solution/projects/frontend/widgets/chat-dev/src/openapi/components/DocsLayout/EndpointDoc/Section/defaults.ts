import type { SectionId } from '../types';

/** Per-HTTP-method defaults for which sections start open. The goal is
 *  "the most useful section is already visible" without burying the
 *  less-important ones entirely.
 *
 *  Rationale by method:
 *    - GET/DELETE: parameters + 2xx response — the request itself has
 *      no body, so that's what the reader needs to see first.
 *    - POST/PUT/PATCH: request body + 2xx response — the shape to send
 *      is the main question; parameters and code samples are
 *      secondary, available one click away.
 *    - Other (HEAD/OPTIONS/…): be conservative, open nothing extra
 *      beyond responses. */
const DEFAULTS_BY_METHOD: Record<string, Partial<Record<SectionId, boolean>>> = {
    GET: { parameters: true, responses: true },
    DELETE: { parameters: true, responses: true },
    POST: { requestBody: true, responses: true },
    PUT: { requestBody: true, responses: true },
    PATCH: { requestBody: true, responses: true },
};

/** Resolve the default open state for a given (method, section). Falls
 *  back to ``false`` for unknown combinations. */
export function defaultSectionOpen(method: string, sectionId: SectionId): boolean {
    return DEFAULTS_BY_METHOD[method.toUpperCase()]?.[sectionId] ?? false;
}
