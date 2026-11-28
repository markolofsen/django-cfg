'use client';

/**
 * Lazy-loaded Combobox Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  ComboboxProps,
  ComboboxTriggerProps,
  ComboboxInputProps,
  ComboboxListProps,
  ComboboxItemProps,
  ComboboxEmptyProps,
} from './types';

export type {
  ComboboxProps,
  ComboboxTriggerProps,
  ComboboxInputProps,
  ComboboxListProps,
  ComboboxItemProps,
  ComboboxEmptyProps,
} from './types';

export const LazyCombobox = createLazyComponent<ComboboxProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.Combobox })),
  {
    displayName: 'LazyCombobox',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazyComboboxTrigger = createLazyComponent<ComboboxTriggerProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.ComboboxTrigger })),
  {
    displayName: 'LazyComboboxTrigger',
    fallback: null,
  }
);

export const LazyComboboxInput = createLazyComponent<ComboboxInputProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.ComboboxInput })),
  {
    displayName: 'LazyComboboxInput',
    fallback: null,
  }
);

export const LazyComboboxList = createLazyComponent<ComboboxListProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.ComboboxList })),
  {
    displayName: 'LazyComboboxList',
    fallback: null,
  }
);

export const LazyComboboxItem = createLazyComponent<ComboboxItemProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.ComboboxItem })),
  {
    displayName: 'LazyComboboxItem',
    fallback: null,
  }
);

export const LazyComboboxEmpty = createLazyComponent<ComboboxEmptyProps>(
  () => import('./parts/Combobox').then((m) => ({ default: m.ComboboxEmpty })),
  {
    displayName: 'LazyComboboxEmpty',
    fallback: null,
  }
);
