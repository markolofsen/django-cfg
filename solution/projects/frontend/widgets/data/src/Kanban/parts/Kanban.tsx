'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ScrollArea } from '@djangocfg/ui-core/components';

import type { KanbanProps } from '../types';
import { KanbanProvider } from '../context/KanbanContext';
import { KanbanColumn } from './KanbanColumn';

export function Kanban(props: KanbanProps) {
  const {
    columns,
    onMoveCard,
    onReorderCard,
    renderCard,
    renderColumnHeader,
    loading,
    emptyColumnMessage,
    className,
    style,
  } = props;

  return (
    <KanbanProvider
      columns={columns}
      onMoveCard={onMoveCard}
      onReorderCard={onReorderCard}
      renderCard={renderCard}
      renderColumnHeader={renderColumnHeader}
      loading={loading}
      emptyColumnMessage={emptyColumnMessage}
    >
      <KanbanShell className={className} style={style} />
    </KanbanProvider>
  );
}
Kanban.displayName = 'Kanban';

function KanbanShell({ className, style }: { className?: string; style?: React.CSSProperties }) {
  const { columns, loading } = useKanbanContext();

  if (loading) {
    return (
      <div
        data-slot="kanban"
        className={cn(
          'flex h-full items-center justify-center rounded-sm border border-border bg-background',
          className
        )}
        style={style}
      >
        <span className="text-muted-foreground">Loading…</span>
      </div>
    );
  }

  return (
    <ScrollArea className="w-full" orientation="horizontal">
      <div
        data-slot="kanban"
        className={cn(
          'flex h-full min-h-[400px] gap-4 rounded-sm border border-border bg-background p-4',
          className
        )}
        style={style}
      >
        {columns.map((column) => (
          <KanbanColumn key={column.id} column={column} />
        ))}
      </div>
    </ScrollArea>
  );
}

// Ambient import for JSX usage
import { useKanbanContext } from '../context/KanbanContext';
