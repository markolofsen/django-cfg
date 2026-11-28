'use client';

import * as React from 'react';
import type { SortableContextValue } from '../types';

const SortableContext = React.createContext<SortableContextValue | null>(null);

export function SortableProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: SortableContextValue;
}) {
  return (
    <SortableContext.Provider value={value}>
      {children}
    </SortableContext.Provider>
  );
}

export function useSortableContext() {
  const context = React.useContext(SortableContext);
  if (!context) {
    throw new Error(
      'useSortableContext must be used within a SortableProvider'
    );
  }
  return context;
}
