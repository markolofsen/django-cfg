'use client';

export { FileIcon } from './FileIcon';
export type { FileIconProps, FileIconSize } from './FileIcon';

export { createFileIconSlot } from './treeAdapter';
export type { CreateFileIconSlotOptions } from './treeAdapter';

export { resolveFolderIcon } from './specialFolders';
export type {
  ResolveFolderIconOptions,
  FolderIconOverrides,
} from './specialFolders';

export { getFileIcon, DEFAULT_FILE_ICON } from './get-file-icon';
export type { FileIconDef } from './get-file-icon';

/** @deprecated Use `getFileIcon` — resolution is now synchronous. */
export { loadMaterialIcons, getMaterialIconsSync } from './loader';
