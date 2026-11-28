'use client';

import { useCallback, useEffect, useRef } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { TreeProvider, useTreeContext } from './context/TreeContext';
import { TreeDndProvider } from './TreeDndProvider';
import { TreeContent, treeRowDomId } from './components/TreeContent';
import { TreeEmptyArea } from './components/TreeEmptyArea';
import { TreeSearchInput } from './components/TreeSearchInput';
import { appearanceToStyle } from './data/appearance';
import {
  useTreeKeyboard,
  useTreeTypeAhead,
  useTreeFinderHotkeys,
} from './hooks';
import type { TreeActionsHandle, TreeRootProps } from './types';

/**
 * High-level entry point. Wraps Provider + (optional) search bar + content.
 *
 * For full control, compose with <TreeProvider>, <TreeContent>,
 * <TreeSearchInput>, <TreeRow>, etc. directly from `@djangocfg/widget-data/tree`.
 */
function TreeRoot<T>(props: TreeRootProps<T>) {
  const {
    data,
    getItemName,
    loadChildren,
    selectionMode,
    activationMode,
    initialExpandedIds,
    initialSelectedIds,
    indent,
    appearance,
    onSelectionChange,
    onExpansionChange,
    onActivate,
    filterNode,
    enableSearch = false,
    enableTypeAhead = true,
    showIndentGuides = false,
    enableInlineRename = false,
    enableFinderHotkeys = false,
    enableDnD = false,
    canDrop,
    renderRow,
    renderIcon,
    renderLabel,
    renderActions,
    renderContextMenu,
    contextMenuActions,
    labels,
    persistKey,
    persistSelection = false,
    adapter,
    defaultMenuItems,
    actionsRef,
    className,
    style,
  } = props;

  return (
    <TreeProvider<T>
      data={data}
      getItemName={getItemName}
      loadChildren={loadChildren}
      selectionMode={selectionMode}
      activationMode={activationMode}
      initialExpandedIds={initialExpandedIds}
      initialSelectedIds={initialSelectedIds}
      indent={indent}
      appearance={appearance}
      onSelectionChange={onSelectionChange}
      onExpansionChange={onExpansionChange}
      onActivate={onActivate}
      filterNode={filterNode}
      enableSearch={enableSearch}
      showIndentGuides={showIndentGuides}
      renderIcon={renderIcon}
      renderLabel={renderLabel}
      renderActions={renderActions}
      // The provider builds the *declarative* merged resolver. Slot
      // conversion happens inside <TreeRootShell /> via the inner ctx,
      // so built-in actions can read live selection state.
      renderContextMenu={renderContextMenu}
      contextMenuActions={contextMenuActions}
      adapter={adapter}
      defaultMenuItems={defaultMenuItems}
      enableInlineRename={enableInlineRename}
      enableDnD={enableDnD}
      canDrop={canDrop}
      labels={labels}
      persistKey={persistKey}
      persistSelection={persistSelection}
    >
      <TreeRootShell<T>
        className={className}
        style={style}
        enableSearch={enableSearch}
        enableTypeAhead={enableTypeAhead}
        enableFinderHotkeys={enableFinderHotkeys}
        renderRow={renderRow}
        actionsRef={actionsRef}
      />
    </TreeProvider>
  );
}

interface TreeRootShellProps<T> {
  className?: string;
  style?: React.CSSProperties;
  enableSearch: boolean;
  enableTypeAhead: boolean;
  enableFinderHotkeys: boolean;
  renderRow?: TreeRootProps<T>['renderRow'];
  actionsRef?: React.MutableRefObject<TreeActionsHandle | null>;
}

function TreeRootShell<T>({
  className,
  style,
  enableSearch,
  enableTypeAhead,
  enableFinderHotkeys,
  renderRow,
  actionsRef,
}: TreeRootShellProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const ctx = useTreeContext<T>();

  // Publish the action handle to the outer ref so host code can call
  // refresh / refreshAll after a mutation that originated outside Tree.
  // Effect runs after mount; the ref stays populated until unmount.
  useEffect(() => {
    if (!actionsRef) return;
    actionsRef.current = {
      refresh: ctx.refresh,
      refreshAll: ctx.refreshAll,
      expandAll: ctx.expandAll,
      collapseAll: ctx.collapseAll,
    };
    return () => {
      if (actionsRef.current) actionsRef.current = null;
    };
  }, [
    actionsRef,
    ctx.refresh,
    ctx.refreshAll,
    ctx.expandAll,
    ctx.collapseAll,
  ]);

  // Keyboard navigation (↑↓ ←→ Home/End Enter Esc Cmd+A, Shift-extend) —
  // scoped via callback ref.
  const isMulti = ctx.selectionMode === 'multiple';
  const { ref: keyboardRef } = useTreeKeyboard<T>({
    rows: ctx.flatRows,
    focusedId: ctx.focused,
    multiSelect: isMulti,
    // Pause container hotkeys while inline rename is active so the
    // user can type freely (TreeRenameInput stops bubbling already, but
    // gating here is the cleaner second line of defence).
    enabled: ctx.renamingId === null,
    onFocus: (id, { extend }) => {
      if (extend && isMulti) {
        ctx.moveSelect(id, { extend: true });
      } else {
        ctx.setFocus(id);
      }
    },
    onSelect: ctx.select,
    onActivate: (id) => {
      // Keyboard Enter / Space is always an explicit action — pin (no preview).
      const row = ctx.flatRows.find((r) => r.node.id === id);
      if (row) ctx.activate(row.node, { preview: false });
    },
    onExpand: ctx.expand,
    onCollapse: ctx.collapse,
    onClearSelection: ctx.clearSelection,
    onSelectAll: ctx.selectAll,
  });

  // Finder hotkeys (P4) — ⌘⌫, F2, ⌘D, ⌘N, ⌘⇧N, ⌘C/X/V. Bound only when
  // `enableFinderHotkeys` is true; individual shortcuts further gated
  // by adapter method availability inside the hook.
  const { ref: finderHotkeysRef } = useTreeFinderHotkeys<T>({
    enabled: enableFinderHotkeys,
    paused: ctx.renamingId !== null,
    adapter: ctx.adapter,
    labels: ctx.labels,
    selected: ctx.selected,
    focused: ctx.focused,
    getNodeById: ctx.getNodeById,
    getItemName: ctx.getItemName,
    startInlineRename: ctx.inlineRenameEnabled ? ctx.startRename : undefined,
    clipboard: {
      hasItems: !!ctx.clipboard && ctx.clipboard.ids.length > 0,
      cut: ctx.cutToClipboard,
      copy: ctx.copyToClipboard,
      // Hotkey paste targets the currently focused row (or null = root).
      paste: () => {
        const target = ctx.focused ? ctx.getNodeById(ctx.focused) ?? null : null;
        return ctx.pasteFromClipboard(target, 'inside');
      },
    },
  });

  const setContainerRef = useCallback(
    (instance: HTMLDivElement | null) => {
      containerRef.current = instance;
      keyboardRef(instance);
      finderHotkeysRef(instance);
    },
    [keyboardRef, finderHotkeysRef],
  );

  // Keep the focused row scrolled into view whenever focus moves (keyboard
  // nav, type-ahead, programmatic). Centralised so every focus source gets
  // consistent scrolling — previously only type-ahead scrolled.
  const focusedId = ctx.focused;
  const isEmpty = ctx.flatRows.length === 0;
  useEffect(() => {
    if (!focusedId) return;
    const el = containerRef.current?.querySelector<HTMLElement>(
      `[data-tree-row][data-id="${CSS.escape(focusedId)}"]`,
    );
    el?.scrollIntoView({ block: 'nearest' });
  }, [focusedId]);

  // Type-ahead jump — focus update; scrolling handled by the effect above.
  const onTypeAheadMatch = useCallback(
    (id: string) => {
      ctx.setFocus(id);
    },
    [ctx],
  );

  useTreeTypeAhead<T>({
    rows: ctx.flatRows,
    getItemName: ctx.getItemName,
    containerRef,
    onMatch: onTypeAheadMatch,
    enabled: enableTypeAhead,
  });

  // Tree body. `ctx.renderContextMenu` is already the final slot —
  // TreeProvider does the declarative→slot merge centrally, so Shell
  // doesn't re-derive it (and no nested provider override is needed).
  const treeBody = (
    <div
      ref={setContainerRef}
      tabIndex={isEmpty ? undefined : 0}
      role={isEmpty ? undefined : 'tree'}
      aria-label={isEmpty ? undefined : ctx.labels.ariaLabel}
      aria-multiselectable={
        !isEmpty && ctx.selectionMode === 'multiple' ? true : undefined
      }
      aria-activedescendant={
        !isEmpty && focusedId ? treeRowDomId(focusedId) : undefined
      }
      className={cn(
        'group/tree flex h-full w-full flex-col gap-2 rounded-sm outline-none',
        'focus-visible:ring-1 focus-visible:ring-ring/50',
        className,
      )}
      style={{ ...appearanceToStyle(ctx.appearance), ...style }}
      data-tree-root=""
    >
      {enableSearch ? <TreeSearchInput className="mx-2 mt-2" /> : null}
      <div className="flex min-h-0 flex-1 flex-col overflow-auto px-1">
        <TreeContent<T> role={isEmpty ? "presentation" : "group"}>
          {renderRow}
        </TreeContent>
        {/* Empty-area: catches right-clicks on whitespace below the
            last row + acts as the root drop target for DnD. Always
            rendered — it self-disables when there's nothing to do. */}
        <TreeEmptyArea />
      </div>
    </div>
  );

  // Wrap in @dnd-kit context only when DnD is active — `TreeDndProvider`
  // short-circuits to a fragment otherwise, so we don't pay the
  // sensor-registration cost.
  return <TreeDndProvider>{treeBody}</TreeDndProvider>;
}

export default TreeRoot;
export { TreeRoot };
