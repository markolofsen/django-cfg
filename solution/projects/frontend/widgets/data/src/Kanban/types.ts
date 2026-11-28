'use client';

import type { ReactNode } from 'react';

export type KanbanCardId = string;
export type KanbanColumnId = string;

export interface KanbanCard {
  id: KanbanCardId;
  title: ReactNode;
  description?: ReactNode;
  /** Extra metadata for custom rendering */
  meta?: Record<string, unknown>;
}

export interface KanbanColumn {
  id: KanbanColumnId;
  title: ReactNode;
  cards: KanbanCard[];
}

export interface KanbanDragState {
  activeCardId: KanbanCardId | null;
  activeColumnId: KanbanColumnId | null;
  overColumnId: KanbanColumnId | null;
  overCardId: KanbanCardId | null;
}

export interface KanbanProps {
  columns: KanbanColumn[];
  /** Called when a card is moved to a different column */
  onMoveCard?: (cardId: KanbanCardId, fromColumnId: KanbanColumnId, toColumnId: KanbanColumnId, toIndex: number) => void;
  /** Called when a card is reordered within the same column */
  onReorderCard?: (columnId: KanbanColumnId, cardId: KanbanCardId, toIndex: number) => void;
  /** Custom card renderer */
  renderCard?: (card: KanbanCard, columnId: KanbanColumnId) => ReactNode;
  /** Custom column header renderer */
  renderColumnHeader?: (column: KanbanColumn) => ReactNode;
  /** Loading state */
  loading?: boolean;
  /** Empty column message */
  emptyColumnMessage?: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}
