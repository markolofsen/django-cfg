'use client';

export interface TreeLabels {
  loading: string;
  empty: string;
  error: string;
  searchPlaceholder: string;
  searchMatches: (count: number) => string;
  ariaLabel: string;

  // ---- CRUD flow copy (used by built-in adapter actions + dialogs) ----

  /** Default context-menu item labels. */
  actionOpen: string;
  actionRename: string;
  actionDuplicate: string;
  actionCut: string;
  actionCopy: string;
  actionPaste: string;
  actionDelete: string;
  actionNewFile: string;
  actionNewFolder: string;

  /** Delete confirmation dialog. */
  confirmDeleteTitle: (count: number) => string;
  confirmDeleteMessage: (names: string[]) => string;
  confirmDeleteOk: string;
  confirmDeleteCancel: string;

  /** New file prompt. */
  newFileTitle: string;
  newFileMessage: string;
  newFilePlaceholder: string;
  newFileDefault: string;

  /** New folder prompt. */
  newFolderTitle: string;
  newFolderMessage: string;
  newFolderPlaceholder: string;
  newFolderDefault: string;

  /** Rename prompt (used when inline rename is unavailable / disabled). */
  renameTitle: string;
  renameMessage: string;

  /** Name validation. */
  invalidNameEmpty: string;

  /** Suffix used by the default `duplicate` flow when the consumer's adapter
   *  needs a hint name. Receives the source name. */
  duplicateSuffix: (name: string) => string;
}

export const DEFAULT_TREE_LABELS: TreeLabels = {
  loading: 'Loading…',
  empty: 'Nothing to show',
  error: 'Failed to load',
  searchPlaceholder: 'Search…',
  searchMatches: (n) => `${n} match${n === 1 ? '' : 'es'}`,
  ariaLabel: 'Tree',

  actionOpen: 'Open',
  actionRename: 'Rename',
  actionDuplicate: 'Duplicate',
  actionCut: 'Cut',
  actionCopy: 'Copy',
  actionPaste: 'Paste',
  actionDelete: 'Delete',
  actionNewFile: 'New file',
  actionNewFolder: 'New folder',

  confirmDeleteTitle: (n) =>
    n === 1 ? 'Delete item?' : `Delete ${n} items?`,
  confirmDeleteMessage: (names) =>
    names.length === 1
      ? `"${names[0]}" will be removed. This action cannot be undone.`
      : `${names.length} items will be removed. This action cannot be undone.`,
  confirmDeleteOk: 'Delete',
  confirmDeleteCancel: 'Cancel',

  newFileTitle: 'New file',
  newFileMessage: 'File name',
  newFilePlaceholder: 'untitled.txt',
  newFileDefault: 'untitled.txt',

  newFolderTitle: 'New folder',
  newFolderMessage: 'Folder name',
  newFolderPlaceholder: 'untitled folder',
  newFolderDefault: 'untitled folder',

  renameTitle: 'Rename',
  renameMessage: 'New name',

  invalidNameEmpty: 'Name cannot be empty',

  duplicateSuffix: (name) => `${name} copy`,
};
