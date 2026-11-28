'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { DataTableProps } from './types';

export const LazyDataTable = createLazyComponent<DataTableProps<unknown>>(
  () => import('./parts/DataTable').then((m) => ({ default: m.DataTable })),
  {
    displayName: 'LazyDataTable',
    fallback: <LoadingFallback minHeight={300} text="Loading data table…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  DataTableProvider,
  useDataTableContext,
} from './context/DataTableContext';
export type {
  DataTableContextValue,
  DataTableProviderProps,
} from './context/DataTableContext';
