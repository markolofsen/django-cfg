'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { ListboxRootProps } from './types';

export const LazyListbox = createLazyComponent<ListboxRootProps>(
  () => import('./context/ListboxProvider').then((m) => ({ default: m.ListboxRoot })),
  {
    displayName: 'LazyListbox',
    fallback: <LoadingFallback minHeight={200} text="Loading listbox…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  ListboxGroup,
  ListboxGroupLabel,
  useListboxGroupContext,
} from './parts/ListboxGroup';
export {
  ListboxItem,
  ListboxItemIndicator,
  useListboxItemContext,
} from './parts/ListboxItem';
export {
  ListboxRoot,
  useListboxContext,
  useListboxState,
  ListboxContext,
} from './context/ListboxProvider';
