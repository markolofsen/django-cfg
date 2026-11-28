// Markdown, code and math — the string-being-streamed layer.
//
// Separate from widgets/ because the input is a STRING ARRIVING TOKEN BY TOKEN,
// not a finished data object. That difference is the whole problem: a
// half-arrived fence must not throw, and a completed message must not re-parse
// because a sibling changed.
//
// One component. The folder is small on purpose — the parser is `streamdown`,
// adopted for exactly one property (it parses incomplete markdown) and pinned
// by tests that would fail if it were swapped back. What lives here is the
// CONFIGURATION of that parser, which is the part that is ours.
//
// May import: core, utils.

export { Response, type ResponseProps } from "./response";
export { renderMediaContent } from "./media-content";
export { ChatAnchor } from "./anchor";
export { safeImageUrl, ZoomableImage, type ZoomableImageProps } from "./zoomable-image";
export { ImageGrid } from "./image-grid";
export { ChatLink, type ChatLinkProps } from "./chat-link";
export { LinkPreviewProvider, resetLinkPreviews, useLinkPreview } from "./link-preview";
