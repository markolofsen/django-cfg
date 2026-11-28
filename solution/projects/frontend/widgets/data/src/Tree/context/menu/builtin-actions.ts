'use client';

import { getDialog } from '@djangocfg/ui-core/lib/dialog-service';
import {
  Copy,
  CornerUpLeft,
  FilePlus,
  FolderPlus,
  Pencil,
  Scissors,
  Trash2,
} from 'lucide-react';
import type { ComponentType } from 'react';

import type {
  TreeAdapter,
  TreeBuiltinAction,
  TreeContextMenuItem,
  TreeItemId,
  TreeLabels,
  TreeNode,
  TreeRowRenderProps,
} from '../../types';

// =====================================================================
// BuiltinActionContext — everything the action handler needs from Tree.
// Kept as a plain object (not a React context) so the same code can be
// shared by hotkeys, right-click menus, and the empty-area menu.
// =====================================================================

export interface BuiltinActionContext<T> {
  adapter: TreeAdapter<T>;
  labels: TreeLabels;
  /** Currently selected nodes (full objects, resolved from ids). */
  selectedNodes: TreeNode<T>[];
  /** Row the user right-clicked / triggered the action on. May be null
   *  for empty-area actions (paste / new file / new folder at root). */
  targetNode: TreeNode<T> | null;
  /** Returns the human-readable name for a node (uses `getItemName`). */
  getName: (node: TreeNode<T>) => string;
  /** Imperative: start inline rename on this id (no-op if disabled). */
  startInlineRename?: (id: TreeItemId) => void;
  /** Clipboard hooks (P5). Provided by Tree's context; pure forwarding. */
  clipboard?: {
    /** Current clipboard kind, if any (so we can hide "Paste" when empty). */
    hasItems: boolean;
    cut: (ids: TreeItemId[]) => void;
    copy: (ids: TreeItemId[]) => void;
    paste: () => void | Promise<void>;
  };
}

interface BuiltinActionDescriptor<T> {
  id: TreeBuiltinAction;
  label: (ctx: BuiltinActionContext<T>) => string;
  icon: ComponentType<{ className?: string }>;
  destructive?: boolean;
  shortcut?: string;
  /** Should this row appear in the menu given the current adapter + selection? */
  available: (ctx: BuiltinActionContext<T>) => boolean;
  run: (ctx: BuiltinActionContext<T>) => Promise<void> | void;
}

// =====================================================================
// Dialog helpers — thin wrappers that bail out gracefully if
// <DialogProvider /> isn't mounted. Tree should still render in that
// case, just without CRUD flows.
// =====================================================================

async function confirmDelete<T>(ctx: BuiltinActionContext<T>): Promise<boolean> {
  const dialog = getDialog();
  if (!dialog) return false;
  const { selectedNodes, labels, getName } = ctx;
  return dialog.confirm({
    title: labels.confirmDeleteTitle(selectedNodes.length),
    message: labels.confirmDeleteMessage(selectedNodes.map(getName)),
    confirmText: labels.confirmDeleteOk,
    cancelText: labels.confirmDeleteCancel,
    variant: 'destructive',
  });
}

async function promptName<T>(
  ctx: BuiltinActionContext<T>,
  spec: {
    title: string;
    message: string;
    placeholder: string;
    defaultValue: string;
  },
): Promise<string | null> {
  const dialog = getDialog();
  if (!dialog) return null;
  return dialog.prompt({
    title: spec.title,
    message: spec.message,
    placeholder: spec.placeholder,
    defaultValue: spec.defaultValue,
  });
}

async function alertError<T>(
  ctx: BuiltinActionContext<T>,
  message: string,
): Promise<void> {
  const dialog = getDialog();
  if (!dialog) return;
  await dialog.alert({ message, title: ctx.labels.error });
}

/**
 * Validate a name through `adapter.validateName` and a tiny built-in
 * non-empty check. Returns `null` if valid, otherwise the error message
 * to surface via `dialog.alert`.
 */
function validateName<T>(
  ctx: BuiltinActionContext<T>,
  name: string,
  validateCtx: { node?: TreeNode<T>; parent?: TreeNode<T> | null },
): string | null {
  if (name.trim() === '') return ctx.labels.invalidNameEmpty;
  return ctx.adapter.validateName?.(name, validateCtx) ?? null;
}

// =====================================================================
// Built-in action descriptors. Order matters — it controls menu order.
// =====================================================================

const BUILTIN_ACTIONS: BuiltinActionDescriptor<unknown>[] = [
  {
    id: 'open',
    label: (ctx) => ctx.labels.actionOpen,
    icon: CornerUpLeft,
    available: () => false, // wired by Tree on activate; not in menu by default
    run: () => {},
  },
  {
    id: 'rename',
    label: (ctx) => ctx.labels.actionRename,
    icon: Pencil,
    shortcut: 'F2',
    available: (ctx) =>
      !!ctx.adapter.rename &&
      ctx.selectedNodes.length === 1 &&
      !ctx.selectedNodes[0]?.disabled,
    run: async (ctx) => {
      // Prefer inline rename when Tree can drive it; fall back to a prompt.
      const node = ctx.selectedNodes[0];
      if (!node) return;
      if (ctx.startInlineRename) {
        ctx.startInlineRename(node.id);
        return;
      }
      const name = await promptName(ctx, {
        title: ctx.labels.renameTitle,
        message: ctx.labels.renameMessage,
        placeholder: ctx.getName(node),
        defaultValue: ctx.getName(node),
      });
      if (name === null) return;
      const err = validateName(ctx, name, { node });
      if (err) return alertError(ctx, err);
      await ctx.adapter.rename!(node, name);
    },
  },
  {
    id: 'duplicate',
    label: (ctx) => ctx.labels.actionDuplicate,
    icon: Copy,
    shortcut: '⌘D',
    available: (ctx) => !!ctx.adapter.duplicate && ctx.selectedNodes.length > 0,
    run: (ctx) => ctx.adapter.duplicate!(ctx.selectedNodes),
  },
  {
    id: 'cut',
    label: (ctx) => ctx.labels.actionCut,
    icon: Scissors,
    shortcut: '⌘X',
    // Only meaningful when the adapter supports `move` (paste-after-cut)
    // AND Tree provided a clipboard binding.
    available: (ctx) =>
      !!ctx.adapter.move && !!ctx.clipboard && ctx.selectedNodes.length > 0,
    run: (ctx) => {
      ctx.clipboard?.cut(ctx.selectedNodes.map((n) => n.id));
    },
  },
  {
    id: 'copy',
    label: (ctx) => ctx.labels.actionCopy,
    icon: Copy,
    shortcut: '⌘C',
    available: (ctx) =>
      !!ctx.adapter.copy && !!ctx.clipboard && ctx.selectedNodes.length > 0,
    run: (ctx) => {
      ctx.clipboard?.copy(ctx.selectedNodes.map((n) => n.id));
    },
  },
  {
    id: 'paste',
    label: (ctx) => ctx.labels.actionPaste,
    icon: CornerUpLeft,
    shortcut: '⌘V',
    available: (ctx) => !!ctx.clipboard?.hasItems,
    run: async (ctx) => {
      await ctx.clipboard?.paste();
    },
  },
  {
    id: 'delete',
    label: (ctx) => ctx.labels.actionDelete,
    icon: Trash2,
    shortcut: '⌘⌫',
    destructive: true,
    available: (ctx) => !!ctx.adapter.remove && ctx.selectedNodes.length > 0,
    run: async (ctx) => {
      const ok = await confirmDelete(ctx);
      if (!ok) return;
      await ctx.adapter.remove!(ctx.selectedNodes);
    },
  },
  {
    id: 'new-file',
    label: (ctx) => ctx.labels.actionNewFile,
    icon: FilePlus,
    available: (ctx) => !!ctx.adapter.createFile,
    run: async (ctx) => {
      const parent = resolveParentForCreate(ctx);
      const name = await promptName(ctx, {
        title: ctx.labels.newFileTitle,
        message: ctx.labels.newFileMessage,
        placeholder: ctx.labels.newFilePlaceholder,
        defaultValue: ctx.labels.newFileDefault,
      });
      if (name === null) return;
      const err = validateName(ctx, name, { parent });
      if (err) return alertError(ctx, err);
      await ctx.adapter.createFile!(parent, name);
    },
  },
  {
    id: 'new-folder',
    label: (ctx) => ctx.labels.actionNewFolder,
    icon: FolderPlus,
    shortcut: '⌘⇧N',
    available: (ctx) => !!ctx.adapter.createFolder,
    run: async (ctx) => {
      const parent = resolveParentForCreate(ctx);
      const name = await promptName(ctx, {
        title: ctx.labels.newFolderTitle,
        message: ctx.labels.newFolderMessage,
        placeholder: ctx.labels.newFolderPlaceholder,
        defaultValue: ctx.labels.newFolderDefault,
      });
      if (name === null) return;
      const err = validateName(ctx, name, { parent });
      if (err) return alertError(ctx, err);
      await ctx.adapter.createFolder!(parent, name);
    },
  },
];

/**
 * Default order of items in the auto-built context menu when the
 * consumer doesn't override `defaultMenuItems`. Separators are
 * conventional Finder/Explorer groupings.
 */
export const DEFAULT_BUILTIN_MENU_ORDER: (TreeBuiltinAction | 'separator')[] = [
  'rename',
  'duplicate',
  'separator',
  'cut',
  'copy',
  'paste',
  'separator',
  'new-file',
  'new-folder',
  'separator',
  'delete',
];

/**
 * Where should a "new file / new folder" land?
 *
 *   - target row is a folder → create inside it
 *   - target row is a leaf   → create as sibling (under its parent)
 *   - no target row          → root (null)
 */
function resolveParentForCreate<T>(ctx: BuiltinActionContext<T>): TreeNode<T> | null {
  const { targetNode } = ctx;
  if (!targetNode) return null;
  // We can't know the parent without walking the tree — Tree passes the
  // target's effective "container" via targetNode for folders; leaves go
  // to root for now. Consumers that need sibling-creation can pass a
  // custom contextMenuActions resolver.
  const isFolder = Array.isArray(targetNode.children) || !!targetNode.isFolder;
  return isFolder ? targetNode : null;
}

/**
 * Build the list of `TreeContextMenuItem`s for the current selection /
 * target row using the configured `defaultMenuItems` (or the default
 * order). Returns `null` when no items are available — caller should
 * suppress the menu entirely.
 */
export function buildDefaultMenuItems<T>(
  ctx: BuiltinActionContext<T>,
  order: (TreeBuiltinAction | 'separator')[] = DEFAULT_BUILTIN_MENU_ORDER,
): TreeContextMenuItem<T>[] | null {
  const items: TreeContextMenuItem<T>[] = [];
  let pendingSeparator = false;

  for (const entry of order) {
    if (entry === 'separator') {
      pendingSeparator = items.length > 0;
      continue;
    }
    const desc = BUILTIN_ACTIONS.find((a) => a.id === entry) as
      | BuiltinActionDescriptor<T>
      | undefined;
    if (!desc) continue;
    if (!desc.available(ctx)) continue;
    if (pendingSeparator) {
      items.push('separator');
      pendingSeparator = false;
    }
    items.push({
      id: desc.id,
      label: desc.label(ctx),
      icon: desc.icon,
      shortcut: desc.shortcut,
      destructive: desc.destructive,
      onSelect: () => void desc.run(ctx),
    });
  }

  return items.length > 0 ? items : null;
}

/**
 * Internal: run a built-in action by id. Used by Finder hotkeys (P4).
 * Returns `false` if the action isn't currently available (e.g. delete
 * with no selection).
 */
export async function runBuiltinAction<T>(
  id: TreeBuiltinAction,
  ctx: BuiltinActionContext<T>,
): Promise<boolean> {
  const desc = BUILTIN_ACTIONS.find((a) => a.id === id) as
    | BuiltinActionDescriptor<T>
    | undefined;
  if (!desc) return false;
  if (!desc.available(ctx)) return false;
  await desc.run(ctx);
  return true;
}

// Re-export typed bits used by callers.
export type { TreeRowRenderProps };
