'use client';

import * as React from 'react';
import type { ColorPickerContextValue } from '../types';

const ColorPickerContext = React.createContext<ColorPickerContextValue | null>(null);

export function useColorPickerContext(consumerName: string) {
  const context = React.useContext(ColorPickerContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within ColorPicker`);
  }
  return context;
}

export function ColorPickerProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: ColorPickerContextValue;
}) {
  return (
    <ColorPickerContext.Provider value={value}>
      {children}
    </ColorPickerContext.Provider>
  );
}
