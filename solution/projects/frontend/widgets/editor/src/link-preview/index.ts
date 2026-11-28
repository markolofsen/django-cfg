/**
 * Surface-agnostic link-preview (URL unfurl) primitives.
 *
 * `LinkPreviewCard` is a pure presentational card (favicon + og:image +
 * title / description / site name) that NEVER fetches the page — it renders
 * pre-resolved `data` or calls a host-provided `resolver(url)`. It is shared
 * across every surface: the chat `LinkBlock` and the NotionEditor `bookmark`
 * node both import it and supply their own resolver. No chat coupling.
 */

export { LinkPreviewCard, type LinkPreviewCardProps } from './LinkPreviewCard';
export type { LinkPreviewData, ResolveLinkPreview } from './types';
