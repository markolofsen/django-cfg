'use client';

import * as React from 'react';
import type { ScrollerContextValue } from '../types';

const ScrollerContext = React.createContext<ScrollerContextValue | null>(null);

export function ScrollerProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: ScrollerContextValue;
}) {
  return (
    <ScrollerContext.Provider value={value}>
      {children}
    </ScrollerContext.Provider>
  );
}

export function useScrollerContext() {
  const context = React.useContext(ScrollerContext);
  if (!context) {
    throw new Error(
      'useScrollerContext must be used within a ScrollerProvider'
    );
  }
  return context;
}
