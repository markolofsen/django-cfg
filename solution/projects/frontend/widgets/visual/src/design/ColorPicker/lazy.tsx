'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { ColorPickerProps } from './types';

export const LazyColorPicker = createLazyComponent<ColorPickerProps>(
  () => import('./ColorPicker').then((mod) => ({ default: mod.ColorPicker })),
  {
    displayName: 'LazyColorPicker',
    fallback: (
      <div className="flex w-[340px] flex-col gap-4 p-4">
        <div className="h-40 w-full animate-pulse rounded-sm bg-muted" />
        <div className="h-3 w-full animate-pulse rounded-full bg-muted" />
        <div className="h-3 w-full animate-pulse rounded-full bg-muted" />
        <div className="flex gap-2">
          <div className="h-8 w-8 animate-pulse rounded-sm bg-muted" />
          <div className="h-8 flex-1 animate-pulse rounded-sm bg-muted" />
        </div>
      </div>
    ),
  }
);

export type { ColorPickerProps } from './types';
