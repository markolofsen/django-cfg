'use client';

import { useCallback, useMemo, useState } from 'react';

import { getDialog } from '@djangocfg/ui-core/lib/dialog-service';

import { defaultCanDrop } from '../../data/dnd';
import type {
  TreeAdapter,
  TreeItemId,
  TreeLabels,
  TreeMovePosition,
  TreeNode,
} from '../../types';

export interface UseDndOptions<T> {
  enabled: boolean;
  adapter?: TreeAdapter<T>;
  nodeById: Map<TreeItemId, TreeNode<T>>;
  /**
   * Multi-selection at the moment dragging begins. If the dragged row
   * is part of the selection, we drag all selected rows; otherwise we
   * drag just the row.
   */
  selected: ReadonlySet<TreeItemId>;
  labels: TreeLabels;
  /** Optional consumer-defined drop validator (layered on top of `defaultCanDrop`). */
  canDrop?: (ctx: {
    source: TreeNode<T>[];
    target: TreeNode<T> | null;
    position: TreeMovePosition;
  }) => boolean;
}

export interface DropTargetState {
  id: TreeItemId | null; // null = root drop zone
  position: TreeMovePosition;
}

export interface UseDndReturn<T> {
  /** True when the host enabled DnD AND adapter.move is defined. */
  active: boolean;
  /** Ids currently being dragged (empty when not dragging). */
  draggingIds: ReadonlySet<TreeItemId>;
  /** Live drop target (`null` when nothing under the pointer). */
  dropTarget: DropTargetState | null;
  /** Called by row sensors on dragstart. */
  beginDrag: (rowId: TreeItemId) => void;
  /**
   * Called on dragover. `null` clears the indicator. Tree already
   * filters self/cycle drops via `defaultCanDrop` — the row component
   * decides the position from pointer geometry first.
   */
  setDropTarget: (target: DropTargetState | null) => void;
  /** Commit drop — calls `adapter.move` and resets transient state. */
  commitDrop: () => Promise<void>;
  /** Cancel without committing (Esc, drop outside). */
  cancelDrag: () => void;
  /**
   * Validate a candidate drop in real time. Combines `defaultCanDrop`
   * with the consumer's `canDrop`. Used by the row component to
   * suppress the indicator on invalid hovers.
   */
  isAllowedDrop: (target: TreeNode<T> | null, position: TreeMovePosition) => boolean;
}

export function useDnd<T>({
  enabled,
  adapter,
  nodeById,
  selected,
  labels,
  canDrop,
}: UseDndOptions<T>): UseDndReturn<T> {
  const active = enabled && !!adapter?.move;

  const [draggingIds, setDraggingIds] = useState<ReadonlySet<TreeItemId>>(
    () => new Set(),
  );
  const [dropTarget, setDropTarget] = useState<DropTargetState | null>(null);

  const beginDrag = useCallback(
    (rowId: TreeItemId) => {
      if (!active) return;
      // If the dragged row is part of the selection, drag the whole
      // selection. Otherwise it's a single-row drag (and we don't
      // touch the existing selection).
      const ids = selected.has(rowId)
        ? new Set(selected)
        : new Set<TreeItemId>([rowId]);
      setDraggingIds(ids);
    },
    [active, selected],
  );

  const cancelDrag = useCallback(() => {
    setDraggingIds(new Set());
    setDropTarget(null);
  }, []);

  const resolveSourceNodes = useCallback((): TreeNode<T>[] => {
    const out: TreeNode<T>[] = [];
    for (const id of draggingIds) {
      const node = nodeById.get(id);
      if (node) out.push(node);
    }
    return out;
  }, [draggingIds, nodeById]);

  const isAllowedDrop = useCallback(
    (target: TreeNode<T> | null, position: TreeMovePosition): boolean => {
      if (!active) return false;
      if (draggingIds.size === 0) return false;
      const source = resolveSourceNodes();
      if (
        !defaultCanDrop<T>({
          source,
          target,
          position,
          getNodeById: (id) => nodeById.get(id),
        })
      ) {
        return false;
      }
      // Layer the consumer's rule on top.
      return canDrop?.({ source, target, position }) ?? true;
    },
    [active, draggingIds, resolveSourceNodes, nodeById, canDrop],
  );

  const commitDrop = useCallback(async () => {
    if (!active || !adapter?.move) {
      cancelDrag();
      return;
    }
    const t = dropTarget;
    if (!t) {
      cancelDrag();
      return;
    }
    const targetNode = t.id ? nodeById.get(t.id) ?? null : null;
    const source = resolveSourceNodes();
    if (source.length === 0) {
      cancelDrag();
      return;
    }
    if (!isAllowedDrop(targetNode, t.position)) {
      cancelDrag();
      return;
    }
    try {
      await adapter.move(source, targetNode, t.position);
    } catch (e) {
      const dialog = getDialog();
      await dialog?.alert({
        title: labels.error,
        message: e instanceof Error ? e.message : String(e),
      });
    } finally {
      cancelDrag();
    }
  }, [
    active,
    adapter,
    cancelDrag,
    dropTarget,
    isAllowedDrop,
    labels,
    nodeById,
    resolveSourceNodes,
  ]);

  return useMemo(
    () => ({
      active,
      draggingIds,
      dropTarget,
      beginDrag,
      setDropTarget,
      commitDrop,
      cancelDrag,
      isAllowedDrop,
    }),
    [
      active,
      draggingIds,
      dropTarget,
      beginDrag,
      commitDrop,
      cancelDrag,
      isAllowedDrop,
    ],
  );
}
