'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ScrollArea } from '@djangocfg/ui-core/components';

import type { KanbanColumn as KanbanColumnType } from '../types';
import { useKanbanContext } from '../context/KanbanContext';
import { KanbanCard } from './KanbanCard';

interface KanbanColumnProps {
  column: KanbanColumnType;
}

export function KanbanColumn({ column }: KanbanColumnProps) {
  const { renderColumnHeader, emptyColumnMessage, dragState, setDragState, moveCard } =
    useKanbanContext();

  const handlePointerEnter = React.useCallback(() => {
    if (dragState.activeCardId && dragState.activeColumnId !== column.id) {
      setDragState((prev) => ({ ...prev, overColumnId: column.id }));
    }
  }, [dragState.activeCardId, dragState.activeColumnId, column.id, setDragState]);

  const handlePointerUp = React.useCallback(() => {
    if (
      dragState.activeCardId &&
      dragState.activeColumnId &&
      dragState.overColumnId === column.id &&
      dragState.activeColumnId !== column.id
    ) {
      const toIndex = column.cards.length;
      moveCard(dragState.activeCardId, dragState.activeColumnId, column.id, toIndex);
    }
    setDragState({
      activeCardId: null,
      activeColumnId: null,
      overColumnId: null,
      overCardId: null,
    });
  }, [dragState, column.id, column.cards.length, moveCard, setDragState]);

  const isOver = dragState.overColumnId === column.id && dragState.activeColumnId !== column.id;

  return (
    <div
      data-slot="kanban-column"
      data-column-id={column.id}
      data-over={isOver ? '' : undefined}
      className={cn(
        'flex w-72 shrink-0 flex-col rounded-sm border border-border bg-muted/30',
        isOver && 'ring-2 ring-ring/50'
      )}
      onPointerEnter={handlePointerEnter}
      onPointerUp={handlePointerUp}
    >
      <div className="border-b border-border bg-muted/50 px-3 py-2">
        {renderColumnHeader ? (
          renderColumnHeader(column)
        ) : (
          <h3 className="text-sm font-semibold text-foreground">{column.title}</h3>
        )}
        <span className="text-xs text-muted-foreground">{column.cards.length} cards</span>
      </div>
      <ScrollArea className="min-h-0 flex-1" viewportClassName="p-2">
        <div className="flex flex-col gap-2">
          {column.cards.length === 0 ? (
            <div className="py-4 text-center text-sm text-muted-foreground">{emptyColumnMessage}</div>
          ) : (
            column.cards.map((card, index) => (
              <KanbanCard key={card.id} card={card} columnId={column.id} index={index} />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
KanbanColumn.displayName = 'KanbanColumn';
