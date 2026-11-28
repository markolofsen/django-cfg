'use client';

import * as React from 'react';

import { useLayoutI18n } from '../../../shared/LayoutI18nProvider';

import { LocaleSwitcherDialog } from './LocaleSwitcherDialog';
import { LocaleSwitcherDropdown } from './LocaleSwitcherDropdown';
import { LocaleSwitcherTrigger } from './LocaleSwitcherTrigger';
import type { LocaleSwitcherVariant } from './types';

export interface LocaleSwitcherProps {
  /**
   * UI flavour.
   * - `dialog` (default): fullscreen language picker with brand header, search, grid.
   * - `dropdown`: compact dropdown menu — best for navbars and dense rails.
   */
  variant?: LocaleSwitcherVariant;
  /** Override / add native names per locale (`{ es: 'Español' }`). */
  labels?: Record<string, string>;

  // Trigger styling — applies to both variants.
  showCode?: boolean;
  buttonVariant?: 'ghost' | 'outline' | 'default';
  size?: 'sm' | 'default' | 'lg' | 'icon';
  /** Show the leading Globe icon when no flag is rendered. @default true */
  showIcon?: boolean;
  /** Show the country flag in the trigger. @default true */
  showFlag?: boolean;
  /** Show the label text in the trigger. @default true */
  showTriggerLabel?: boolean;
  /** Extra trigger className. */
  className?: string;
}

/**
 * Locale switcher with two flavours: a compact dropdown and a fullscreen
 * dialog. Pulls `locale` / `locales` / `onChange` / `brand` / `dialogLabels`
 * from `LayoutI18nProvider` (mounted by `BaseApp`) — no need to thread them
 * through props.
 */
export function LocaleSwitcher({
  variant = 'dialog',
  labels,
  className,
  showCode = false,
  buttonVariant = 'ghost',
  size = 'sm',
  showIcon = true,
  showFlag = true,
  showTriggerLabel = true,
}: LocaleSwitcherProps) {
  const i18n = useLayoutI18n();
  const [open, setOpen] = React.useState(false);

  if (variant === 'dropdown') {
    return (
      <LocaleSwitcherDropdown
        locale={i18n.locale}
        locales={i18n.locales}
        onChange={i18n.onLocaleChange}
        labels={labels}
        className={className}
        showCode={showCode}
        variant={buttonVariant}
        size={size}
        showIcon={showIcon}
        showFlag={showFlag}
        showTriggerLabel={showTriggerLabel}
      />
    );
  }

  return (
    <>
      <LocaleSwitcherTrigger
        locale={i18n.locale}
        labels={labels}
        showFlag={showFlag}
        showLabel={showTriggerLabel}
        showCode={showCode}
        variant={buttonVariant}
        size={size}
        className={className}
        ariaLabel={i18n.dialogLabels?.triggerLabel ?? 'Change language'}
        onClick={() => setOpen(true)}
      />
      <LocaleSwitcherDialog
        locale={i18n.locale}
        locales={i18n.locales}
        onChange={i18n.onLocaleChange}
        labels={labels}
        i18nLabels={i18n.dialogLabels}
        brand={i18n.brand}
        open={open}
        onOpenChange={setOpen}
      />
    </>
  );
}
