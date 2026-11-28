/**
 * The rich-text editors and the pieces both are built from.
 *
 * Deliberately NOT a barrel over everything: TipTap is sixteen packages and
 * the two editors do not share a consumer. An app wanting the markdown field
 * must not resolve the Notion editor's tables, drag handle and syntax
 * highlighter behind it.
 *
 * Import a subpath: `@djangocfg/widget-editor/markdown`,
 * `@djangocfg/widget-editor/notion`, `/blocks`, `/link-preview`, `/chips`.
 */
export type { MarkdownEditorProps } from './markdown';
