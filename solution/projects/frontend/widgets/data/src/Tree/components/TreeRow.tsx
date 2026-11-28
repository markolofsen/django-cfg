'use client';

import { Loader2 } from 'lucide-react';
import { memo, useCallback } from 'react';
import { useDraggable, useDroppable } from '@dnd-kit/core';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';
import { radiusClass, rowStateClasses } from '../data/appearance';
import type { FlatRow, TreeRowRenderProps } from '../types';
import { TreeChevron } from './TreeChevron';
import { treeRowDomId } from './TreeContent';
import { TreeDropIndicator } from './TreeDropIndicator';
import { TreeIcon } from './TreeIcon';
import { TreeIndentGuides } from './TreeIndentGuides';
import { TreeLabel } from './TreeLabel';
import { TreeRenameInput } from './TreeRenameInput';

export interface TreeRowProps<T> {
  row: FlatRow<T>;
  className?: string;
}

/**
 * TreeRow — single row in a virtualised tree.
 *
 * Memoised: re-renders only when `row` reference or `className` change.
 * `row` is treated as immutable — the parent should not mutate node
 * objects in place.
 */
function TreeRowRaw<T>({ row, className }: TreeRowProps<T>) {
  const ctx = useTreeContext<T>();
  const {
    appearance,
    activationMode,
    showIndentGuides,
    selected,
    focused,
    matchingIds,
    select,
    setSelectedIds,
    clickSelect,
    toggle,
    setFocus,
    activate,
    getItemName,
    renderIcon,
    renderLabel,
    renderActions,
    renderContextMenu,
    renamingId,
    commitRename,
    cancelRename,
    clipboard,
    dnd,
  } = ctx;

  const { node, level, isFolder, isExpanded, isLoading, posInSet, setSize } = row;
  const isSelected = selected.has(node.id);
  const isFocused = focused === node.id;
  const isMatchingSearch = matchingIds.has(node.id);
  const isMultiSelect = ctx.selectionMode === 'multiple';
  const isCut =
    clipboard?.kind === 'cut' && clipboard.ids.includes(node.id);

  const slot: TreeRowRenderProps<T> = {
    node,
    level,
    isSelected,
    isExpanded,
    isFocused,
    isFolder,
    isLoading,
    isMatchingSearch,
  };

  // Folders always toggle on single click regardless of `activationMode`.
  // Leaves dispatch by mode:
  //   single-click          → click activates {preview:false}
  //   double-click          → click only selects; dblclick activates {preview:false}
  //   single-click-preview  → click activates {preview:true}; dblclick activates {preview:false}
  const isRenaming = renamingId === node.id;
  const isDragging = dnd.draggingIds.has(node.id);
  const dropTarget = dnd.dropTarget;
  const isDropTarget = dropTarget?.id === node.id;
  const dropPosition = isDropTarget ? dropTarget!.position : null;

  // ─── DnD wiring ──────────────────────────────────────────────────
  // Hooks are called unconditionally so we don't violate rules-of-
  // hooks; the `disabled` flag short-circuits @dnd-kit when DnD is off
  // or the row is in inline rename.
  //
  // Drop-zone resolution (before/inside/after) is centralised in
  // `<TreeDndProvider>` via `onDragMove` — rows don't need a
  // `onPointerMove` of their own. Saves a listener × N rows.
  const dndDisabled = !dnd.active || isRenaming || node.disabled;
  const draggable = useDraggable({ id: node.id, disabled: dndDisabled });
  /**
   * dnd-kit's DESCRIPTIVE aria only.
   *
   * `draggable.attributes` also carries `role: 'button'`, `tabIndex: 0` and
   * `aria-disabled`, and it was spread AFTER this row's own attributes — so
   * while drag was enabled the row stopped being a `treeitem` (a tree of
   * buttons announces as a list of buttons) and every row became tab-stoppable,
   * defeating the roving tabindex the keyboard navigation depends on. tsc
   * reported it as three duplicate props; the symptom was only audible.
   */
  const dragAria = {
    'aria-roledescription': draggable.attributes['aria-roledescription'],
    'aria-describedby': draggable.attributes['aria-describedby'],
    'aria-pressed': draggable.attributes['aria-pressed'],
  };
  const droppable = useDroppable({ id: node.id, disabled: dndDisabled });

  const setRowEl = useCallback(
    (el: HTMLDivElement | null) => {
      draggable.setNodeRef(el);
      droppable.setNodeRef(el);
    },
    [draggable, droppable],
  );

  const isAllowedDrop =
    dropPosition && !isDragging
      ? dnd.isAllowedDrop(node, dropPosition)
      : true;
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (node.disabled || isRenaming) return;
    setFocus(node.id);
    // Multi-select: full Finder/Explorer semantics — plain replaces, meta
    // toggles, shift extends range from anchor, shift+meta unions range.
    // Single-select: clickSelect collapses to {id}. None: no-op.
    if (isMultiSelect) {
      clickSelect(node.id, { shift: e.shiftKey, meta: e.metaKey || e.ctrlKey });
    } else {
      select(node.id);
    }
    if (isFolder) {
      // Don't toggle on shift/meta clicks — those are pure selection edits.
      if (e.shiftKey || e.metaKey || e.ctrlKey) return;
      toggle(node.id);
    } else if (activationMode === 'single-click') {
      // Selection-only modifier clicks should not activate the leaf.
      if (e.shiftKey || e.metaKey || e.ctrlKey) return;
      activate(node, { preview: false });
    } else if (activationMode === 'single-click-preview') {
      if (e.shiftKey || e.metaKey || e.ctrlKey) return;
      activate(node, { preview: true });
    }
  };

  const handleDoubleClick = () => {
    if (node.disabled || isRenaming) return;
    if (isFolder) return;
    activate(node, { preview: false });
  };

  // Finder/Explorer semantics: right-click on an unselected row switches
  // selection to that single row (so menu actions apply to it). Right-
  // click on a row already in the selection leaves the multi-selection
  // intact (so destructive bulk actions stay safe).
  const handleContextMenu = () => {
    if (node.disabled || isRenaming) return;
    setFocus(node.id);
    if (!isSelected) {
      setSelectedIds([node.id]);
    }
  };

  const trigger = (
    <div
      ref={dnd.active ? setRowEl : undefined}
      id={treeRowDomId(node.id)}
      role="treeitem"
      aria-level={level + 1}
      aria-posinset={posInSet}
      aria-setsize={setSize}
      aria-expanded={isFolder ? isExpanded : undefined}
      aria-selected={ctx.selectionMode === 'none' ? undefined : isSelected}
      aria-disabled={node.disabled || undefined}
      data-tree-row=""
      data-id={node.id}
      data-activation-mode={activationMode}
      data-selected={isSelected ? 'true' : undefined}
      data-clipboard={isCut ? 'cut' : undefined}
      data-dragging={isDragging ? 'true' : undefined}
      data-focused={isFocused && !isSelected ? 'true' : undefined}
      data-folder={isFolder || undefined}
      data-expanded={isExpanded || undefined}
      tabIndex={-1}
      style={{
        paddingLeft: 6 + level * appearance.indent,
        // `auto` sizing lets a multi-line label (e.g. title + meta in a
        // chat-history list) grow the row instead of overflowing a fixed
        // height. `fixed` keeps the classic single-line explorer row.
        ...(appearance.rowSizing === 'auto'
          ? {
              minHeight: 'var(--tree-row-height)',
              paddingTop: 4,
              paddingBottom: 4,
            }
          : { height: 'var(--tree-row-height)' }),
        gap: 'var(--tree-gap)',
      }}
      {...(dnd.active ? draggable.listeners : {})}
      {...(dnd.active ? dragAria : {})}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onContextMenu={handleContextMenu}
      onFocus={() => setFocus(node.id)}
      className={cn(
        'group/row relative flex w-full select-none items-center pr-2 text-left',
        'transition-colors outline-none',
        node.disabled ? 'cursor-not-allowed' : 'cursor-pointer',
        radiusClass(appearance),
        rowStateClasses(appearance),
        'focus-visible:ring-1 focus-visible:ring-ring/50',
        isMatchingSearch && 'ring-1 ring-primary/30',
        isCut && 'opacity-60',
        isDragging && 'opacity-40',
        node.disabled && 'opacity-50',
        className,
      )}
    >
      {/* Active-row left indicator (VSCode style) */}
      {appearance.showActiveIndicator && isSelected ? (
        <span
          aria-hidden
          className={cn(
            'absolute left-0 top-1 bottom-1 w-0.5 rounded-r-full',
            'bg-foreground/30 group-focus-within/tree:bg-primary',
          )}
        />
      ) : null}

      {/* DnD drop indicator — top/bottom line for sibling reorder,
          fill for "drop into folder". */}
      {dropPosition && !isDragging ? (
        <TreeDropIndicator
          position={dropPosition}
          indent={6 + level * appearance.indent}
          invalid={!isAllowedDrop}
        />
      ) : null}

      {showIndentGuides && level > 0 ? (
        <TreeIndentGuides level={level} indent={appearance.indent} />
      ) : null}

      <TreeChevron isExpanded={isExpanded} isFolder={isFolder} />

      {isLoading ? (
        <Loader2
          aria-hidden
          strokeWidth={appearance.iconStrokeWidth}
          style={{ width: 'var(--tree-icon-size)', height: 'var(--tree-icon-size)' }}
          className="shrink-0 animate-spin text-muted-foreground/70"
        />
      ) : renderIcon ? (
        renderIcon(slot)
      ) : (isFolder ? appearance.hideFolderIcons : appearance.hideLeafIcons) ? null : (
        <TreeIcon isFolder={isFolder} isExpanded={isExpanded} />
      )}

      <span
        className="flex min-w-0 flex-1 items-center"
        style={{ gap: 'var(--tree-gap)' }}
      >
        {renamingId === node.id ? (
          <TreeRenameInput
            initialValue={getItemName(node)}
            isFolder={isFolder}
            onCommit={(next) => commitRename(node.id, next)}
            onCancel={cancelRename}
          />
        ) : renderLabel ? (
          renderLabel(slot)
        ) : (
          <TreeLabel isMatchingSearch={isMatchingSearch}>{getItemName(node)}</TreeLabel>
        )}
      </span>

      {renderActions ? (
        <span
          className="ml-auto flex shrink-0 items-center gap-1 opacity-0 transition-opacity group-hover/row:opacity-100 group-focus-within/row:opacity-100"
          onClick={(e) => e.stopPropagation()}
        >
          {renderActions(slot)}
        </span>
      ) : null}
    </div>
  );

  if (renderContextMenu) {
    return <>{renderContextMenu(slot, trigger)}</>;
  }
  return trigger;
}

export const TreeRow = memo(TreeRowRaw) as typeof TreeRowRaw;
