'use client';

import type { TreeNode, TreeRowSlot } from '../Tree/types';
import { FileIcon, type FileIconSize } from './FileIcon';
import type { FolderIconOverrides } from './specialFolders';

export interface CreateFileIconSlotOptions<T> {
  /**
   * How to read the displayed name (with extension) for a node. Use the same
   * accessor you pass to `<TreeRoot getItemName={...} />`.
   */
  getName: (node: TreeNode<T>) => string;
  /** Pixel size for both file and folder icons. Default: 16. */
  size?: FileIconSize;
  /**
   * Override or extend the built-in special-folder mapping (e.g. give
   * `tests` a custom icon). Keys are matched case-insensitively.
   */
  folderOverrides?: FolderIconOverrides;
}

/**
 * Build a `renderIcon` slot for `<TreeRoot>` that uses `<FileIcon>` for both
 * leaves and folders.
 *
 * @example
 * ```tsx
 * <TreeRoot
 *   data={data}
 *   getItemName={(n) => n.data.name}
 *   renderIcon={createFileIconSlot({ getName: (n) => n.data.name })}
 * />
 * ```
 */
export function createFileIconSlot<T>({
  getName,
  size = 16,
  folderOverrides,
}: CreateFileIconSlotOptions<T>): TreeRowSlot<T> {
  // Named so the slot shows as `FileIconSlot` in React devtools rather than
  // as an anonymous function.
  const FileIconSlot: TreeRowSlot<T> = ({ node, isFolder, isExpanded }) => (
    <FileIcon
      name={getName(node)}
      isFolder={isFolder}
      isExpanded={isExpanded}
      size={size}
      folderOverrides={folderOverrides}
    />
  );
  return FileIconSlot;
}
