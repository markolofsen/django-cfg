// Media blocks: the eleven-kind vocabulary and the `src` allowlist.
//
// Pure TypeScript, no React — the allowlist is a SECURITY BOUNDARY and belongs
// where it can be tested exhaustively without a renderer. It is a deliberate
// mirror of the server's media vocabulary and allowlist, not a shared helper:
// the server gates what a tool may emit, this gates what a browser will load,
// and a stored transcript reaches the DOM with no live server process
// re-checking it.

export { attachmentIdOf, isAllowedSrc, cleanPath } from "./allowed-src";
export type { SameOriginPrefixes } from "./allowed-src";

export { MEDIA_KINDS, isMediaKind, TEXTUAL_KINDS, SRC_KINDS, URL_FIELDS } from "./kinds";
export type { MediaKind } from "./kinds";

export { readMediaBlock } from "./block";
export type {
  MediaBlock,
  MediaGalleryItem,
  MediaGeneration,
  MediaLinkPreview,
} from "./block";
