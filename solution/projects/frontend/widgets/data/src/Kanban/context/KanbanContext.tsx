'use client';

import * as React from 'react';
import {
  createContext,
  useCallback,
  useMemo,
  useState,
} from 'react';

import type {
  KanbanCard,
  KanbanCardId,
  KanbanColumn,
  KanbanColumnId,
  KanbanDragState,
  KanbanProps,
} from '../types';

// =====================================================================
// Context value
// =====================================================================

export interface KanbanContextValue {
  columns: KanbanColumn[];
  dragState: KanbanDragState;
  setDragState: React.Dispatch<React.SetStateAction<KanbanDragState>>;
  moveCard: (cardId: KanbanCardId, fromColumnId: KanbanColumnId, toColumnId: KanbanColumnId, toIndex: number) => void;
  reorderCard: (columnId: KanbanColumnId, cardId: KanbanCardId, toIndex: number) => void;
  renderCard?: (card: KanbanCard, columnId: KanbanColumnId) => React.ReactNode;
  renderColumnHeader?: (column: KanbanColumn) => React.ReactNode;
  loading: boolean;
  emptyColumnMessage: React.ReactNode;
}

const KanbanContext = createContext<KanbanContextValue | null>(null);

export function useKanbanContext(): KanbanContextValue {
  const ctx = React.useContext(KanbanContext);
  if (!ctx) {
    throw new Error('useKanbanContext must be used inside <KanbanProvider>');
  }
  return ctx;
}

// =====================================================================
// Provider
// =====================================================================

export interface KanbanProviderProps
  extends Pick<
    KanbanProps,
    | 'columns'
    | 'onMoveCard'
    | 'onReorderCard'
    | 'renderCard'
    | 'renderColumnHeader'
    | 'loading'
    | 'emptyColumnMessage'
  > {
  children: React.ReactNode;
}

export function KanbanProvider(props: KanbanProviderProps) {
  const {
    columns: initialColumns,
    onMoveCard,
    onReorderCard,
    renderCard,
    renderColumnHeader,
    loading = false,
    emptyColumnMessage = 'No cards',
    children,
  } = props;

  const [columns, setColumns] = useState<KanbanColumn[]>(initialColumns);
  const [dragState, setDragState] = useState<KanbanDragState>({
    activeCardId: null,
    activeColumnId: null,
    overColumnId: null,
    overCardId: null,
  });

  // Sync with external columns prop
  React.useEffect(() => {
    setColumns(initialColumns);
  }, [initialColumns]);

  const moveCard = useCallback(
    (cardId: KanbanCardId, fromColumnId: KanbanColumnId, toColumnId: KanbanColumnId, toIndex: number) => {
      setColumns((prev) => {
        const next = prev.map((col) => ({ ...col, cards: [...col.cards] }));
        const fromCol = next.find((c) => c.id === fromColumnId);
        const toCol = next.find((c) => c.id === toColumnId);
        if (!fromCol || !toCol) return prev;

        const cardIndex = fromCol.cards.findIndex((c) => c.id === cardId);
        if (cardIndex === -1) return prev;

        const [card] = fromCol.cards.splice(cardIndex, 1);
        if (!card) return prev;
        const insertIndex = Math.min(toIndex, toCol.cards.length);
        toCol.cards.splice(insertIndex, 0, card);

        return next;
      });
      onMoveCard?.(cardId, fromColumnId, toColumnId, toIndex);
    },
    [onMoveCard],
  );

  const reorderCard = useCallback(
    (columnId: KanbanColumnId, cardId: KanbanCardId, toIndex: number) => {
      setColumns((prev) => {
        const next = prev.map((col) =>
          col.id === columnId ? { ...col, cards: [...col.cards] } : col,
        );
        const col = next.find((c) => c.id === columnId);
        if (!col) return prev;

        const fromIndex = col.cards.findIndex((c) => c.id === cardId);
        if (fromIndex === -1 || fromIndex === toIndex) return prev;

        const [card] = col.cards.splice(fromIndex, 1);
        if (!card) return prev;
        const insertIndex = Math.min(toIndex, col.cards.length);
        col.cards.splice(insertIndex, 0, card);

        return next;
      });
      onReorderCard?.(columnId, cardId, toIndex);
    },
    [onReorderCard],
  );

  const value = useMemo<KanbanContextValue>(
    () => ({
      columns,
      dragState,
      setDragState,
      moveCard,
      reorderCard,
      renderCard,
      renderColumnHeader,
      loading,
      emptyColumnMessage,
    }),
    [
      columns,
      dragState,
      moveCard,
      reorderCard,
      renderCard,
      renderColumnHeader,
      loading,
      emptyColumnMessage,
    ],
  );

  return (
    <KanbanContext.Provider value={value}>
      {children}
    </KanbanContext.Provider>
  );
}
