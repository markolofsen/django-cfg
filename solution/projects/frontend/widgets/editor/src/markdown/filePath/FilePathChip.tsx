'use client';

/**
 * `<FilePathChip>` — a compact, presentational chip for a LOCAL file path
 * (Cursor / VSCode / Finder style): the extension-correct file icon +
 * a smart middle-ellipsized label, monospace, with the full path on hover.
 *
 * Standalone by design — it imports only the pure detector helpers and the
 * shared `FileIcon`, so it can render a known path in a chat message,
 * a file list, etc., entirely outside the TipTap editor.
 *
 * Presentational only: it never mutates or links anything. Inside the
 * editor the SAME visual is reproduced by the `editorChip` atom NODE
 * (see `../chip/ChipNode.ts`, `kind: 'path'`) — this component is the
 * React/standalone counterpart, still useful for rendering a known path
 * outside the editor (chat messages, file lists).
 */

import { cn } from '@djangocfg/ui-core/lib';
import { FileIcon } from '@djangocfg/widget-data/file-icon';
import { splitPath, truncatePathLabel } from './detect';

export interface FilePathChipProps {
  /** The full, raw file path (Unix / macOS / Windows / UNC / `file://`). */
  path: string;
  /**
   * Approximate max characters for the truncated label. The basename is
   * always preserved; only the middle collapses. Default 40.
   */
  maxChars?: number;
  /** Icon size in px. Default 14 (matches inline text). */
  iconSize?: 12 | 14 | 16;
  className?: string;
}

/**
 * Render a path as an inline chip. Uses the folder icon when the path
 * resolves to a directory (no file extension / trailing separator).
 */
export function FilePathChip({
  path,
  maxChars = 40,
  iconSize = 14,
  className,
}: FilePathChipProps) {
  const { base, isDir } = splitPath(path);
  const label = truncatePathLabel(path, { maxChars });

  return (
    <span
      className={cn(
        // Inline pill: muted surface + border, monospace, semantic tokens
        // only (mirrors the inline-code look). `max-w` + `truncate` is the
        // CSS safety net under the semantic middle-ellipsis label.
        'inline-flex max-w-[22rem] items-center gap-1 rounded',
        'border border-border bg-muted px-1.5 py-0.5 align-baseline',
        'font-mono text-[0.8125em] leading-tight text-foreground',
        className,
      )}
      title={path}
    >
      <FileIcon name={base} isFolder={isDir} size={iconSize} />
      <span className="truncate">{label}</span>
    </span>
  );
}

export default FilePathChip;
