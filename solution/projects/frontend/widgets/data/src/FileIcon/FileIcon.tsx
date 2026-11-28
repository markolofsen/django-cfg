'use client';

import { cn } from '@djangocfg/ui-core/lib';

import { getFileIcon } from './get-file-icon';
import { resolveFolderIcon, type FolderIconOverrides } from './specialFolders';

export type FileIconSize = 12 | 14 | 16 | 18 | 20 | 24 | 28 | 32 | 40 | 48 | 64;

export interface FileIconProps {
  /** File name (with extension) or folder name. */
  name: string;
  /** Render a folder icon instead of a file icon. */
  isFolder?: boolean;
  /** Folder open / closed state. Ignored when `isFolder` is false. */
  isExpanded?: boolean;
  /** Pixel size of the icon. */
  size?: FileIconSize;
  /**
   * Override or extend the built-in special-folder mapping. Keys are
   * matched case-insensitively. Only used when `isFolder` is true.
   */
  folderOverrides?: FolderIconOverrides;
  /**
   * Accessible label. When omitted the icon is decorative (`aria-hidden`) —
   * correct when it sits next to a visible file name. Pass a string to
   * expose the icon to assistive technology.
   */
  label?: string;
  className?: string;
}

/**
 * VSCode-style file icon.
 *
 * - Folders render Lucide `Folder` / `FolderOpen` (warning-token tint).
 * - Files render rich, colourful SVGs vendored from `material-file-icons`
 *   (MIT). Resolution is synchronous — no runtime dependency, no async load.
 *
 * The icon SVG data is a static module, so it bundles into the `FileIcon`
 * chunk and is only fetched by consumers that actually mount this component.
 */
export function FileIcon({
  name,
  isFolder = false,
  isExpanded = false,
  size = 16,
  folderOverrides,
  label,
  className,
}: FileIconProps) {
  // Either a labelled image, or fully hidden from assistive tech (the default,
  // since the icon usually sits beside a visible file name).
  const a11y =
    label === undefined
      ? ({ 'aria-hidden': true } as const)
      : ({ role: 'img', 'aria-label': label } as const);

  if (isFolder) {
    const Icon = resolveFolderIcon({
      name,
      isExpanded,
      overrides: folderOverrides,
    });
    return (
      <Icon
        {...a11y}
        className={cn('shrink-0 text-warning', className)}
        style={{ width: size, height: size }}
      />
    );
  }

  // Vendored static data — `getFileIcon` always returns a definition.
  const svg = getFileIcon(name).svg;

  return (
    <span
      {...a11y}
      className={cn('inline-block shrink-0', className)}
      style={{ width: size, height: size }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

export default FileIcon;
