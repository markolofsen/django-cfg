'use client';

import type { ComponentType, ReactNode } from 'react';

import type { TreeNode } from './node';

export interface TreeRowRenderProps<T> {
  node: TreeNode<T>;
  level: number;
  isSelected: boolean;
  isExpanded: boolean;
  isFocused: boolean;
  isFolder: boolean;
  isLoading: boolean;
  isMatchingSearch: boolean;
}

export type TreeRowSlot<T> = (props: TreeRowRenderProps<T>) => ReactNode;

export type TreeContextMenuSlot<T> = (
  props: TreeRowRenderProps<T>,
  trigger: ReactNode,
) => ReactNode;

/**
 * Declarative context-menu item. Pass `'separator'` (string) in place of an
 * object to insert a `<ContextMenuSeparator />` between groups.
 *
 * For more advanced needs (submenus, checkbox items, custom JSX), drop down
 * to `renderContextMenu` instead.
 */
export interface TreeContextMenuAction<T> {
  /** Stable React key. */
  id: string;
  label: ReactNode;
  /** Lucide-style icon component. Rendered as `<icon className="size-4" />`. */
  icon?: ComponentType<{ className?: string }>;
  /** Right-aligned keyboard hint (e.g. `'⌘C'`, `'↵'`). Cosmetic. */
  shortcut?: ReactNode;
  /** Disable the item — still rendered, not selectable. */
  disabled?: boolean;
  /** Style as destructive (red). */
  destructive?: boolean;
  /** Click / Enter handler. Receives the row meta. */
  onSelect: (props: TreeRowRenderProps<T>) => void;
}

export type TreeContextMenuItem<T> = TreeContextMenuAction<T> | 'separator';

/**
 * Context passed to a `contextMenuActions` resolver. `row` is the row the
 * user right-clicked. `selectedNodes` is the multi-selection at the
 * moment the menu opens — when the right-clicked row was not in the
 * selection, Tree first switches selection to that single row, so
 * `selectedNodes` always contains the right-clicked node.
 */
export interface TreeContextMenuActionsContext<T> extends TreeRowRenderProps<T> {
  /** Multi-selection at the moment the menu opens. Always non-empty. */
  selectedNodes: TreeNode<T>[];
}

export type TreeContextMenuActionsResolver<T> = (
  ctx: TreeContextMenuActionsContext<T>,
) => TreeContextMenuItem<T>[] | null | undefined;
