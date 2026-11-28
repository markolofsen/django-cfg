'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { GripVertical } from 'lucide-react';
import { SortableProvider, useSortableContext } from '../context';
import type {
  SortableProps,
  SortableItemProps,
  SortableHandleProps,
} from '../types';

export function Sortable({
  children,
  items,
  onReorder,
  axis = 'vertical',
  handleOnly = true,
  className,
}: SortableProps) {
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const moveItem = React.useCallback(
    (activeId: string, overId: string) => {
      const activeIndex = items.findIndex((i) => i.id === activeId);
      const overIndex = items.findIndex((i) => i.id === overId);
      if (activeIndex === -1 || overIndex === -1 || activeIndex === overIndex) return;
      const newItems = [...items];
      // `activeIndex` came from `findIndex` and is in range, so the splice yields one item.
      const [removed] = newItems.splice(activeIndex, 1);
      if (removed === undefined) return;
      newItems.splice(overIndex, 0, removed);
      onReorder(newItems);
    },
    [items, onReorder]
  );

  const value = React.useMemo(
    () => ({
      items,
      activeId,
      axis,
      handleOnly,
      setActiveId,
      moveItem,
    }),
    [items, activeId, axis, handleOnly, moveItem]
  );

  return (
    <SortableProvider value={value}>
      <div
        ref={containerRef}
        data-slot="sortable"
        data-axis={axis}
        className={cn(
          'flex',
          axis === 'vertical' ? 'flex-col' : 'flex-row',
          className
        )}
      >
        {children}
      </div>
    </SortableProvider>
  );
}
Sortable.displayName = 'Sortable';

export function SortableItem({ id, children, className, ...props }: SortableItemProps) {
  const { activeId, handleOnly, setActiveId, moveItem } = useSortableContext();
  const isActive = activeId === id;
  const itemRef = React.useRef<HTMLDivElement>(null);

  const onPointerDown = React.useCallback(
    (e: React.PointerEvent) => {
      if (handleOnly) return; // drag only via handle
      const target = e.target as HTMLElement;
      if (target.closest('[data-slot="sortable-handle"]')) return;
      e.preventDefault();
      setActiveId(id);
    },
    [handleOnly, id, setActiveId]
  );

  const onPointerEnter = React.useCallback(() => {
    if (activeId && activeId !== id) {
      moveItem(activeId, id);
    }
  }, [activeId, id, moveItem]);

  return (
    <div
      ref={itemRef}
      data-slot="sortable-item"
      data-id={id}
      data-active={isActive ? 'true' : undefined}
      onPointerDown={onPointerDown}
      onPointerEnter={onPointerEnter}
      className={cn(
        'relative select-none transition-transform',
        isActive && 'z-50 opacity-80 scale-[1.02]',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
SortableItem.displayName = 'SortableItem';

export function SortableHandle({ children, className, ...props }: SortableHandleProps) {
  const { setActiveId } = useSortableContext();

  const onPointerDown = React.useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault();
      const item = (e.currentTarget as HTMLElement).closest('[data-id]');
      if (item) {
        const id = item.getAttribute('data-id');
        if (id) setActiveId(id);
      }
    },
    [setActiveId]
  );

  return (
    <div
      data-slot="sortable-handle"
      onPointerDown={onPointerDown}
      className={cn(
        'cursor-grab active:cursor-grabbing inline-flex items-center justify-center',
        'text-muted-foreground hover:text-foreground transition-colors',
        className
      )}
      {...props}
    >
      {children ?? <GripVertical className="h-4 w-4" />}
    </div>
  );
}
SortableHandle.displayName = 'SortableHandle';
