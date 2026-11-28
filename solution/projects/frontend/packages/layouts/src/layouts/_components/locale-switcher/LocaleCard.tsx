'use client';

import * as React from 'react';
import { Check } from 'lucide-react';

import { LanguageFlag } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import type { LocaleMeta } from './localeMeta';

export interface LocaleCardProps {
  code: string;
  meta: LocaleMeta;
  active: boolean;
  onSelect: (code: string) => void;
  /** Compact list-row layout used on small viewports. @default false (grid tile) */
  compact?: boolean;
}

/**
 * One locale tile. Two flavours: spacious grid tile (desktop) and compact
 * list row (mobile). Both share the same flag + native + english structure.
 */
export const LocaleCard = React.memo(function LocaleCard({
  code,
  meta,
  active,
  onSelect,
  compact = false,
}: LocaleCardProps) {
  const handleClick = React.useCallback(() => {
    onSelect(code);
  }, [code, onSelect]);

  const baseClass = cn(
    'group relative flex w-full cursor-pointer items-center gap-3 rounded-xl border text-left transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 focus-visible:ring-offset-1 focus-visible:ring-offset-background',
    active
      ? 'border-primary bg-primary/[0.06] ring-1 ring-primary/25'
      : 'border-border/60 bg-card hover:border-primary/40 hover:bg-accent/40',
  );

  if (compact) {
    return (
      <button
        type="button"
        onClick={handleClick}
        aria-current={active ? 'true' : undefined}
        className={cn(baseClass, 'min-h-[56px] px-3.5 py-2.5')}
      >
        <LanguageFlag
          code={code}
          rounded
          className="h-5 w-7 shrink-0 shadow-[0_0_0_1px_rgb(0_0_0/0.06)]"
        />
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium text-foreground">{meta.native}</div>
          {meta.english && meta.english !== meta.native && (
            <div className="truncate text-xs text-muted-foreground">{meta.english}</div>
          )}
        </div>
        {active && <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />}
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-current={active ? 'true' : undefined}
      dir={meta.rtl ? 'rtl' : undefined}
      className={cn(baseClass, 'min-h-[88px] flex-col items-start gap-2 px-4 py-3.5 sm:min-h-[96px]')}
    >
      <div className="flex w-full items-center justify-between">
        <LanguageFlag
          code={code}
          rounded
          className="h-6 w-9 shadow-[0_0_0_1px_rgb(0_0_0/0.08)]"
        />
        {active && <Check className="h-4 w-4 text-primary" aria-hidden />}
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-semibold text-foreground">{meta.native}</div>
        {meta.english && meta.english !== meta.native && (
          <div className="truncate text-xs text-muted-foreground">{meta.english}</div>
        )}
      </div>
    </button>
  );
});
