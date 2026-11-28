// Viewers presented inside a conversation or a file preview.
//
// The root barrel exports the image viewer ONLY. `./diagram`, `./markdown` and
// `./code` are subpath-only on purpose: each pulls a parser or a highlighter
// (mermaid ~2.5 MB, shiki, katex), and a host mounting a lightbox must not pay
// for any of them. A barrel re-export is a static edge — naming them here would
// undo the split silently.
export * from "./image-viewer";
export type { MediaCopy } from "./i18n";
export { DEFAULT_MEDIA_COPY, MEDIA_DICTIONARIES, useMediaCopy } from "./i18n";
