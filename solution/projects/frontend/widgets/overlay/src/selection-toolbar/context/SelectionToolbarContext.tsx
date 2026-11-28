'use client';

import * as React from 'react';
import type { SelectionToolbarContextValue } from '../types';

const SelectionToolbarContext = React.createContext<SelectionToolbarContextValue | null>(null);

export function SelectionToolbarProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: SelectionToolbarContextValue;
}) {
  return (
    <SelectionToolbarContext.Provider value={value}>
      {children}
    </SelectionToolbarContext.Provider>
  );
}

export function useSelectionToolbarContext() {
  const context = React.useContext(SelectionToolbarContext);
  if (!context) {
    throw new Error(
      'useSelectionToolbarContext must be used within a SelectionToolbarProvider'
    );
  }
  return context;
}
