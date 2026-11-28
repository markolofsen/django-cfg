'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { DataGridProps } from './types';

export const LazyDataGrid = createLazyComponent<DataGridProps<unknown>>(
  () => import('./parts/DataGrid').then((m) => ({ default: m.DataGrid })),
  {
    displayName: 'LazyDataGrid',
    fallback: <LoadingFallback minHeight={300} text="Loading data grid…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  DataGridProvider,
  useDataGridContext,
} from './context/DataGridContext';
export type {
  DataGridContextValue,
  DataGridProviderProps,
} from './context/DataGridContext';
