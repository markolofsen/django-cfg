/**
 * Surface-agnostic presentational "chips" — compact inline pills that
 * render a URL or a file path with a favicon/icon + middle-ellipsis label.
 *
 * These match the TipTap composer's `editorChip` look (see
 * `forms/MarkdownEditor/chip/ChipNode.ts`) but are plain React, so the same
 * visual is reusable across every surface (composer, chat bubble, lists).
 *
 * - `UrlChip`      — clickable URL chip (favicon → globe fallback).
 * - `FilePathChip` — local file-path chip (re-exported from the editor's
 *   standalone path chip; it's already presentational/dependency-light, so
 *   we wrap rather than duplicate).
 */
export { UrlChip, default as UrlChipDefault } from './UrlChip';
export type { UrlChipProps } from './UrlChip';

export {
  FilePathChip,
  type FilePathChipProps,
} from '../markdown/filePath/FilePathChip';
