'use client';

import type * as React from 'react';

export type SortableAxis = 'vertical' | 'horizontal';

export interface SortableItemData {
  id: string;
}

export interface SortableContextValue {
  items: SortableItemData[];
  activeId: string | null;
  axis: SortableAxis;
  handleOnly: boolean;
  setActiveId: (id: string | null) => void;
  moveItem: (activeId: string, overId: string) => void;
}

export interface SortableProps {
  children: React.ReactNode;
  /** Items with unique ids */
  items: SortableItemData[];
  /** Called when order changes */
  onReorder: (items: SortableItemData[]) => void;
  /** Drag axis */
  axis?: SortableAxis;
  /** Only allow dragging via handle */
  handleOnly?: boolean;
  className?: string;
}

export interface SortableItemProps extends React.HTMLAttributes<HTMLDivElement> {
  id: string;
  children: React.ReactNode;
}

export interface SortableHandleProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}
