'use client';

import * as React from 'react';
import type { ComboboxContextValue } from '../types';

const ComboboxContext = React.createContext<ComboboxContextValue | null>(null);

export function ComboboxProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: ComboboxContextValue;
}) {
  return (
    <ComboboxContext.Provider value={value}>
      {children}
    </ComboboxContext.Provider>
  );
}

export function useComboboxContext() {
  const context = React.useContext(ComboboxContext);
  if (!context) {
    throw new Error(
      'useComboboxContext must be used within a ComboboxProvider'
    );
  }
  return context;
}
