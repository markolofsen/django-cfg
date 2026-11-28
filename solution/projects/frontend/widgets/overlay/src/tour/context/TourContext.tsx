'use client';

import * as React from 'react';
import type { TourContextValue } from '../types';

const TourContext = React.createContext<TourContextValue | null>(null);

export function TourProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: TourContextValue;
}) {
  return (
    <TourContext.Provider value={value}>
      {children}
    </TourContext.Provider>
  );
}

export function useTourContext() {
  const context = React.useContext(TourContext);
  if (!context) {
    throw new Error(
      'useTourContext must be used within a TourProvider'
    );
  }
  return context;
}
