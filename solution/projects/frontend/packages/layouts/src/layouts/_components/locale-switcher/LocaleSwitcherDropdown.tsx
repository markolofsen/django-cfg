'use client';

import * as React from 'react';
import { Globe } from 'lucide-react';

import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  LanguageFlag,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { ICON_FLAG_CLASS } from './iconFlag';
import { getLocaleMeta } from './localeMeta';
import type { LocaleSwitcherSharedProps } from './types';

export interface LocaleSwitcherDropdownProps extends LocaleSwitcherSharedProps {
  showCode?: boolean;
  variant?: 'ghost' | 'outline' | 'default';
  size?: 'sm' | 'default' | 'lg' | 'icon';
  showIcon?: boolean;
  showFlag?: boolean;
  showTriggerLabel?: boolean;
}

/**
 * Compact dropdown locale switcher — kept for navbar and dense layouts where
 * a fullscreen dialog feels heavy.
 */
export function LocaleSwitcherDropdown({
  locale,
  locales,
  onChange,
  labels,
  showCode = false,
  variant = 'ghost',
  size = 'sm',
  showIcon = true,
  showFlag = true,
  showTriggerLabel = true,
  className,
}: LocaleSwitcherDropdownProps) {
  const currentMeta = getLocaleMeta(locale, labels);
  const currentLabel = showCode ? locale.toUpperCase() : currentMeta.native;
  const isIconOnly = size === 'icon';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        {isIconOnly ? (
          <Button
            variant={variant}
            size={size}
            aria-label={currentLabel}
            className={cn('overflow-hidden rounded-full p-0', className)}
          >
            {showFlag ? (
              <LanguageFlag code={locale} rounded className={ICON_FLAG_CLASS} />
            ) : (
              <Globe className="h-4 w-4" aria-hidden />
            )}
          </Button>
        ) : (
          <Button variant={variant} size={size} className={className}>
            {showFlag ? (
              <LanguageFlag
                code={locale}
                rounded
                className={cn('h-3 w-4 shrink-0', showTriggerLabel && 'mr-1.5')}
              />
            ) : showIcon ? (
              <Globe className={cn('h-4 w-4 shrink-0', showTriggerLabel && 'mr-1')} />
            ) : null}
            {showTriggerLabel && <span>{currentLabel}</span>}
          </Button>
        )}
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="border-white/10 bg-popover/60 backdrop-blur-2xl backdrop-saturate-150"
      >
        {locales.map((code) => {
          const meta = getLocaleMeta(code, labels);
          const active = code === locale;
          return (
            <DropdownMenuItem
              key={code}
              onClick={() => onChange(code)}
              className={cn(
                'flex items-center gap-2',
                active && 'bg-accent',
              )}
            >
              {showFlag && <LanguageFlag code={code} rounded className="h-3 w-4 shrink-0" />}
              <span>{showCode ? `${code.toUpperCase()} - ${meta.native}` : meta.native}</span>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
