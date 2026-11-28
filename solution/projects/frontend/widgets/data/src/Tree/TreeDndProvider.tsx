'use client';

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragMoveEvent,
  type DragStartEvent,
} from '@dnd-kit/core';
import { useCallback, useRef } from 'react';

import { useTreeContext } from './context/TreeContext';
import { resolveDropZone, TREE_ROOT_DROP_ID } from './data/dnd';
import type { TreeItemId } from './types';

interface TreeDndProviderProps {
  children: React.ReactNode;
}

/**
 * Wrap Tree's body in a `<DndContext>` when DnD is enabled.
 *
 * One central drag handler decides the drop zone (`before` / `inside` /
 * `after`) from the cursor position vs. the hovered row's bounding box.
 * Rows themselves only register `useDraggable` + `useDroppable` — no
 * per-row `onPointerMove`, so dragging across 1000 rows stays cheap.
 *
 * Sensors: pointer (with a small activation distance so a plain click
 * doesn't initiate a drag) + keyboard (drag with Space/Enter, arrows,
 * Space drops — built-in accessibility).
 */
export function TreeDndProvider({ children }: TreeDndProviderProps) {
  const ctx = useTreeContext();
  const { dnd } = ctx;

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor),
  );

  // Latest cursor position — @dnd-kit gives us the active rectangle but
  // not the raw pointer Y. We grab it from pointermove ourselves and
  // use it inside `onDragMove` to compute the drop zone.
  const cursorYRef = useRef(0);

  const handleDragStart = useCallback(
    (e: DragStartEvent) => {
      dnd.beginDrag(e.active.id as TreeItemId);
    },
    [dnd],
  );

  const handleDragMove = useCallback(
    (e: DragMoveEvent) => {
      const overId = e.over?.id;
      // Root drop target — TreeEmptyArea registers under this id.
      if (overId === TREE_ROOT_DROP_ID) {
        const current = dnd.dropTarget;
        if (current?.id !== null || current?.position !== 'inside') {
          dnd.setDropTarget({ id: null, position: 'inside' });
        }
        return;
      }
      if (typeof overId !== 'string') {
        if (dnd.dropTarget !== null) dnd.setDropTarget(null);
        return;
      }

      // The dnd-kit `over.rect` is the droppable's bounding box. Combined
      // with the latest cursor Y we recover the same before/inside/after
      // split Finder uses.
      const rect = e.over?.rect;
      if (!rect) return;

      // `data-folder` on the dom row tells us if `inside` is allowed.
      const el = document.querySelector<HTMLElement>(
        `[data-tree-row][data-id="${CSS.escape(overId)}"]`,
      );
      const isFolder = el?.dataset.folder === 'true';

      const position = resolveDropZone({
        pointerY: cursorYRef.current,
        rowRect: { top: rect.top, bottom: rect.top + rect.height, height: rect.height },
        isFolder,
      });

      const current = dnd.dropTarget;
      if (current?.id !== overId || current.position !== position) {
        dnd.setDropTarget({ id: overId, position });
      }
    },
    [dnd],
  );

  const handleDragEnd = useCallback(
    async (_e: DragEndEvent) => {
      await dnd.commitDrop();
    },
    [dnd],
  );

  const handleDragCancel = useCallback(() => {
    dnd.cancelDrag();
  }, [dnd]);

  // Track the latest cursor Y position globally while a drag is in flight.
  // Used by `handleDragMove` to figure out which third of the row we're
  // over. Cheap — one passive listener, no re-renders.
  const handlePointerMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    cursorYRef.current = e.clientY;
  }, []);

  if (!dnd.active) {
    return <>{children}</>;
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragMove={handleDragMove}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div
        onPointerMove={handlePointerMove}
        className="contents"
        data-tree-dnd-surface=""
      >
        {children}
      </div>
    </DndContext>
  );
}
