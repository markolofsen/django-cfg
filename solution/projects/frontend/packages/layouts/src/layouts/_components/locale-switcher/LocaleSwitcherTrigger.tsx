'use client';

import * as React from 'react';
import { Globe } from 'lucide-react';

import { Button, LanguageFlag } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { ICON_FLAG_CLASS } from './iconFlag';
import { getLocaleMeta } from './localeMeta';

export interface LocaleSwitcherTriggerProps {
  locale: string;
  labels?: Record<string, string>;
  /** Show the flag in the trigger. @default true */
  showFlag?: boolean;
  /** Show the locale label / native name in the trigger. @default true */
  showLabel?: boolean;
  /** Show locale code instead of the native name (`'EN'` instead of `'English'`). */
  showCode?: boolean;
  variant?: 'ghost' | 'outline' | 'default';
  size?: 'sm' | 'default' | 'lg' | 'icon';
  className?: string;
  ariaLabel?: string;
  onClick?: () => void;
}

/**
 * Footer / navbar trigger that opens the dialog. Visually matches the
 * existing dropdown trigger so swapping `variant` does not shift the row.
 */
export const LocaleSwitcherTrigger = React.forwardRef<
  HTMLButtonElement,
  LocaleSwitcherTriggerProps
>(function LocaleSwitcherTrigger(
  {
    locale,
    labels,
    showFlag = true,
    showLabel = true,
    showCode = false,
    variant = 'outline',
    size = 'default',
    className,
    ariaLabel,
    onClick,
  },
  ref,
) {
  const meta = getLocaleMeta(locale, labels);
  const labelText = showCode ? locale.toUpperCase() : meta.native;
  const isIconOnly = size === 'icon';

  // Icon-only trigger: a fixed-size flag centred in the button.
  if (isIconOnly) {
    return (
      <Button
        ref={ref}
        type="button"
        variant={variant}
        size={size}
        onClick={onClick}
        aria-label={ariaLabel ?? labelText}
        className={cn(
          'overflow-hidden rounded-full p-0',
          className,
        )}
      >
        {showFlag ? (
          <LanguageFlag
            code={locale}
            rounded
            className={ICON_FLAG_CLASS}
          />
        ) : (
          <Globe className="h-4 w-4" aria-hidden />
        )}
      </Button>
    );
  }

  return (
    <Button
      ref={ref}
      type="button"
      variant={variant}
      size={size}
      onClick={onClick}
      aria-label={ariaLabel}
      className={cn('inline-flex items-center gap-2', className)}
    >
      {showFlag ? (
        <LanguageFlag
          code={locale}
          rounded
          className="h-3 w-4 shrink-0"
        />
      ) : (
        <Globe className="h-4 w-4 shrink-0" aria-hidden />
      )}
      {showLabel && <span className="truncate">{labelText}</span>}
    </Button>
  );
});
