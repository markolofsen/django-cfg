'use client';

import * as React from 'react';
import type { ResponsiveDialogContextValue } from '../types';

const ResponsiveDialogContext = React.createContext<ResponsiveDialogContextValue | null>(null);

export function ResponsiveDialogProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: ResponsiveDialogContextValue;
}) {
  return (
    <ResponsiveDialogContext.Provider value={value}>
      {children}
    </ResponsiveDialogContext.Provider>
  );
}

export function useResponsiveDialogContext() {
  const context = React.useContext(ResponsiveDialogContext);
  if (!context) {
    throw new Error(
      'useResponsiveDialogContext must be used within a ResponsiveDialogProvider'
    );
  }
  return context;
}
