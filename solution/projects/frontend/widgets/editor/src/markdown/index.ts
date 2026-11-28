export { MarkdownEditor } from './MarkdownEditor';
export type { MarkdownEditorProps, MarkdownEditorHandle } from './MarkdownEditor';
export type {
  MentionItem,
  MentionConfig,
  MentionAttrs,
  MentionMarkdownRenderer,
} from './types';
export { mentionPresets } from './mentionPresets';
export type { SlashCommandInfo } from './slash/types';

// File-path chip — the standalone presentational chip plus the pure
// detector helpers (usable outside the editor, e.g. rendering a known
// path in a chat message).
export { FilePathChip } from './filePath/FilePathChip';
export type { FilePathChipProps } from './filePath/FilePathChip';
export { findFilePaths, splitPath, truncatePathLabel } from './filePath/detect';
export type { FilePathMatch, SplitPath, TruncateOptions } from './filePath/detect';

// URL chip — pure detector + display helpers backing the in-editor URL chip
// (the `editorChip` node's `kind: 'url'`). Usable standalone too.
export {
  findUrls,
  splitUrl,
  truncateUrlLabel,
  faviconUrl,
  normalizeHref,
} from './url/detect';
export type { UrlMatch, SplitUrl, UrlLabelOptions } from './url/detect';
