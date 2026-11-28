/**
 * Local types for the EndpointDoc folder. Wider OpenAPI types live in
 * ``../../../types``; this module only declares what's specific to the
 * docs-view rendering (section identifiers, tab ids, etc.).
 */

/** Sections a single endpoint card can contain. Section identity is
 *  stable because zustand stores open/close state keyed by it, and the
 *  URL hash router references sections by the same id. */
export type SectionId = 'parameters' | 'requestBody' | 'responses' | 'codeSamples';

export const ALL_SECTION_IDS: readonly SectionId[] = [
    'parameters',
    'requestBody',
    'responses',
    'codeSamples',
] as const;
