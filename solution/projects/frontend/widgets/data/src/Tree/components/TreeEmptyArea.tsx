'use client';

import { useMemo } from 'react';
import { useDroppable } from '@dnd-kit/core';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';
import {
  buildDefaultMenuItems,
  type BuiltinActionContext,
} from '../context/menu';
import { TREE_ROOT_DROP_ID } from '../data/dnd';
import type { TreeContextMenuItem } from '../types';

export interface TreeEmptyAreaProps {
  className?: string;
}

/**
 * Fills the remaining vertical space below `<TreeContent>` so the user
 * can right-click "into nothing" to get a Finder/Explorer-style empty
 * area menu (paste / new file / new folder at root), and so DnD has a
 * root drop target.
 *
 * Built-in actions are derived the same way as for rows — through
 * `buildDefaultMenuItems`, with `targetNode = null` (root) and
 * `selectedNodes = []` (nothing under the right-click). Items whose
 * `available()` predicate fails are simply skipped, so a tree without
 * `adapter.createFile/Folder` and without a clipboard payload shows
 * no menu at all.
 */
export function TreeEmptyArea({ className }: TreeEmptyAreaProps) {
  const ctx = useTreeContext();
  const {
    adapter,
    labels,
    getItemName,
    clipboard,
    cutToClipboard,
    copyToClipboard,
    pasteFromClipboard,
    startRename,
    inlineRenameEnabled,
    dnd,
  } = ctx;

  // Root drop target — receives drops that miss every row. The shared
  // `TreeDndProvider.onDragMove` detects when `e.over.id === ROOT_DROP_ID`
  // and pushes `{ id: null, position: 'inside' }` into `dnd.dropTarget`,
  // so this component doesn't need an `onPointerMove` of its own.
  const { setNodeRef: setDroppableRef, isOver } = useDroppable({
    id: TREE_ROOT_DROP_ID,
    disabled: !dnd.active,
  });

  // Resolve menu items every render — they depend on clipboard state
  // (paste shows/hides) and on whether the adapter exposes
  // createFile / createFolder.
  const items = useMemo<TreeContextMenuItem<unknown>[] | null>(() => {
    if (!adapter) return null;
    const builtinCtx: BuiltinActionContext<unknown> = {
      adapter,
      labels,
      selectedNodes: [],
      targetNode: null,
      getName: getItemName,
      startInlineRename: inlineRenameEnabled ? startRename : undefined,
      clipboard: {
        hasItems: !!clipboard && clipboard.ids.length > 0,
        cut: cutToClipboard,
        copy: copyToClipboard,
        paste: () => pasteFromClipboard(null, 'inside'),
      },
    };
    return buildDefaultMenuItems(builtinCtx);
  }, [
    adapter,
    labels,
    getItemName,
    inlineRenameEnabled,
    startRename,
    clipboard,
    cutToClipboard,
    copyToClipboard,
    pasteFromClipboard,
  ]);

  const surface = (
    <div
      ref={dnd.active ? setDroppableRef : undefined}
      data-tree-empty-area=""
      data-drop-active={dnd.active && isOver ? 'true' : undefined}
      className={cn(
        // Soaks up the remaining vertical space inside the scroll
        // container so right-click on whitespace lands here, not on
        // the scroll viewport.
        'min-h-[2.5rem] flex-1',
        dnd.active && isOver && 'bg-primary/5 rounded-sm ring-1 ring-primary/30',
        className,
      )}
    />
  );

  // No items and no DnD overlap → render plain spacer. Wrapping in a
  // `<ContextMenu>` with zero items would still capture right-clicks
  // and show an empty popover — that's worse than browser default.
  if (!items || items.length === 0) {
    return surface;
  }

  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>{surface}</ContextMenuTrigger>
      <ContextMenuContent>
        {items.map((item, idx) => {
          if (item === 'separator') {
            return <ContextMenuSeparator key={`sep-${idx}`} />;
          }
          const Icon = item.icon;
          return (
            <ContextMenuItem
              key={item.id}
              disabled={item.disabled}
              variant={item.destructive ? 'destructive' : undefined}
              // Pass a synthetic "no-target" row props — the built-in
              // action handlers we surface here (new-file / new-folder
              // / paste) don't read row-specific fields anyway.
              onSelect={() =>
                item.onSelect({
                  node: undefined as never,
                  level: 0,
                  isSelected: false,
                  isExpanded: false,
                  isFocused: false,
                  isFolder: false,
                  isLoading: false,
                  isMatchingSearch: false,
                })
              }
            >
              {Icon ? <Icon /> : null}
              {item.label}
              {item.shortcut ? (
                <ContextMenuShortcut>{item.shortcut}</ContextMenuShortcut>
              ) : null}
            </ContextMenuItem>
          );
        })}
      </ContextMenuContent>
    </ContextMenu>
  );
}
