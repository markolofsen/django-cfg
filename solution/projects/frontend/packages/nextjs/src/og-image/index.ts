// ── Recommended API ──────────────────────────────────────────────────────────
// Bind the factory once per app, then call it from each page.
export { createMetadata, makeMetadataFactory } from './metadata-factory'
export type { SiteMetaConfig, PageMeta } from './metadata-factory'

// ── Types ────────────────────────────────────────────────────────────────────
export type { OgSpec } from './types'

// ── Low-level primitives (escape hatches) ────────────────────────────────────
export { resolveOgImage, extractTitle } from './metadata'
