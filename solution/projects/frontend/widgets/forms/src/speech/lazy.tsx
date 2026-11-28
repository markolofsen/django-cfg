'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { DictationFieldProps } from './widgets/DictationField';

export const LazyDictationField = createLazyComponent<DictationFieldProps>(
  () =>
    import('./widgets/DictationField').then((mod) => ({
      default: mod.DictationField,
    })),
  {
    displayName: 'LazyDictationField',
    fallback: (
      <div className="rounded-lg border border-border/60 bg-card px-3 py-2 text-xs text-muted-foreground">
        Loading dictation…
      </div>
    ),
  },
);
