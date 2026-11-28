// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { ColorPaletteProps } from './types';

export const LazyColorPalette = createLazyComponent<ColorPaletteProps>(
  () => import('./ColorPalette').then((m) => ({ default: m.ColorPalette })),
  {
    displayName: 'LazyColorPalette',
    fallback: (
      <div
        data-slot="color-palette-skeleton"
        className="grid h-32 animate-pulse gap-3 rounded-lg bg-muted"
      />
    ),
  },
);

export type { ColorPaletteProps } from './types';
