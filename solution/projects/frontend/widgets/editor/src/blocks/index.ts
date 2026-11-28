/**
 * Shared block payload types — the serializable wire shapes that both the
 * chat message blocks and the NotionEditor block NodeViews reference, so the
 * shapes can't drift. The link-preview data shape lives in
 * `common/link-preview`; the map payload lives here. Re-exported below so a
 * single import (`common/blocks`) reaches every shared block payload.
 */

export type {
  MapBlockPayload,
  MapMarkerPayload,
  MapRoutePayload,
  MapPolygonPayload,
} from './types';

// Re-export the link-preview data contract from its home so consumers can
// reach every shared block payload from one place.
export type { LinkPreviewData, ResolveLinkPreview } from '../link-preview';

// Runtime validators + the safe-render fallback. A block NodeView/renderer
// parses its payload through the matching schema and renders `<BlockError>`
// on failure instead of throwing.
export {
  MapMarkerPayloadSchema,
  MapRoutePayloadSchema,
  MapPolygonPayloadSchema,
  MapBlockPayloadSchema,
  LinkPreviewDataSchema,
  safeParseBlock,
} from './schemas';
export type { SafeParseResult } from './schemas';

export { BlockError } from './BlockError';
export type { BlockErrorProps } from './BlockError';
