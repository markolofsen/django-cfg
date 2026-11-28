/**
 * Shared TipTap helpers — reusable across every NotionEditor block NodeView.
 *
 * `useNodeAttrs` is the write-back seam an interactive NodeView uses to push UI
 * changes (drag a pin, switch a basemap) back into the document's node attrs,
 * so the change survives the markdown round-trip.
 */

export { useNodeAttrs } from './useNodeAttrs';
export type { UseNodeAttrsResult } from './useNodeAttrs';
