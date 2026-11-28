// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { TYPE_TAG_CLASSES } from '../types';
import { classifyTypeToken, splitTypeSignature } from '../utils';

interface TypeDisplayProps {
  type: string;
  className?: string;
}

/**
 * Render a type signature with per-token semantic colorization. Splits
 * on `|`, classifies each token via {@link classifyTypeToken}, and maps
 * the classification to a semantic `text-*` token from
 * {@link TYPE_TAG_CLASSES}.
 */
export function TypeDisplay({ type, className }: TypeDisplayProps) {
  const parts = React.useMemo(() => splitTypeSignature(type), [type]);

  return (
    <span className={cn('font-mono text-sm', className)} data-slot="api-ref-type">
      {parts.map((part, i) => {
        const trimmed = part.trim();
        if (trimmed === '|') {
          return (
            <span key={i} className="text-muted-foreground">
              {' | '}
            </span>
          );
        }
        const tag = classifyTypeToken(trimmed);
        return (
          <span key={i} className={TYPE_TAG_CLASSES[tag]} data-type-tag={tag}>
            {trimmed}
          </span>
        );
      })}
    </span>
  );
}
