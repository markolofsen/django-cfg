'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import type { KanbanCard as KanbanCardType, KanbanColumnId } from '../types';
import { useKanbanContext } from '../context/KanbanContext';

interface KanbanCardProps {
  card: KanbanCardType;
  columnId: KanbanColumnId;
  index: number;
}

export function KanbanCard({ card, columnId, index }: KanbanCardProps) {
  const { renderCard, dragState, setDragState, moveCard, reorderCard } = useKanbanContext();
  const isActive = dragState.activeCardId === card.id;
  const isOver = dragState.overCardId === card.id && dragState.activeCardId !== card.id;

  const handlePointerDown = React.useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault();
      setDragState({
        activeCardId: card.id,
        activeColumnId: columnId,
        overColumnId: null,
        overCardId: null,
      });
    },
    [card.id, columnId, setDragState],
  );

  const handlePointerEnter = React.useCallback(() => {
    if (!dragState.activeCardId || dragState.activeCardId === card.id) return;

    setDragState((prev) => ({ ...prev, overCardId: card.id, overColumnId: columnId }));

    if (dragState.activeColumnId === columnId) {
      reorderCard(columnId, dragState.activeCardId, index);
    } else if (dragState.activeColumnId) {
      moveCard(dragState.activeCardId, dragState.activeColumnId, columnId, index);
      setDragState((prev) => ({ ...prev, activeColumnId: columnId }));
    }
  }, [card.id, columnId, index, dragState, setDragState, reorderCard, moveCard]);

  return (
    <div
      data-slot="kanban-card"
      data-id={card.id}
      data-column-id={columnId}
      data-active={isActive ? '' : undefined}
      data-over={isOver ? '' : undefined}
      onPointerDown={handlePointerDown}
      onPointerEnter={handlePointerEnter}
      className={cn(
        'cursor-grab select-none rounded-sm border border-border bg-background p-3 shadow-sm',
        'transition-all',
        'hover:border-primary/50',
        isActive && 'z-50 scale-[1.02] opacity-80 shadow-lg',
        isOver && 'border-dashed border-primary'
      )}
    >
      {renderCard ? (
        renderCard(card, columnId)
      ) : (
        <>
          <h4 className="text-sm font-medium text-foreground">{card.title}</h4>
          {card.description && (
            <p className="mt-1 text-xs text-muted-foreground">{card.description}</p>
          )}
        </>
      )}
    </div>
  );
}
KanbanCard.displayName = 'KanbanCard';
