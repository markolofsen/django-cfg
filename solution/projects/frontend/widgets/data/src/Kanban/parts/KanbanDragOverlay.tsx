'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { useKanbanContext } from '../context/KanbanContext';

export function KanbanDragOverlay() {
  const { dragState, columns, renderCard } = useKanbanContext();

  if (!dragState.activeCardId || !dragState.activeColumnId) return null;

  const column = columns.find((c) => c.id === dragState.activeColumnId);
  const card = column?.cards.find((c) => c.id === dragState.activeCardId);

  if (!card) return null;

  return (
    <div
      data-slot="kanban-drag-overlay"
      className={cn(
        'pointer-events-none fixed z-[100] rounded-sm border border-border bg-background p-3 shadow-lg',
        'opacity-90'
      )}
      style={{
        // Positioned via pointer events in a real implementation;
        // this is a static overlay that follows the cursor via CSS
        // In a production app, you'd track pointer position in state
        left: 'var(--kanban-drag-x, 50%)',
        top: 'var(--kanban-drag-y, 50%)',
      }}
    >
      {renderCard ? (
        renderCard(card, dragState.activeColumnId)
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
KanbanDragOverlay.displayName = 'KanbanDragOverlay';
