'use client';

import * as React from 'react';
import type { ScrollSpyContextValue } from '../types';

const ScrollSpyContext = React.createContext<ScrollSpyContextValue | null>(null);

export function ScrollSpyProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: ScrollSpyContextValue;
}) {
  return (
    <ScrollSpyContext.Provider value={value}>
      {children}
    </ScrollSpyContext.Provider>
  );
}

export function useScrollSpyContext() {
  const context = React.useContext(ScrollSpyContext);
  if (!context) {
    throw new Error(
      'useScrollSpyContext must be used within a ScrollSpyProvider'
    );
  }
  return context;
}
