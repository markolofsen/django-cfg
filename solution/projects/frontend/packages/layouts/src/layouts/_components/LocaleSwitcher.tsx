/**
 * Re-export shim — kept for backwards compatibility with code that imports
 * `LocaleSwitcher` / `LOCALE_LABELS` from this path.
 *
 * The implementation now lives in `./locale-switcher/`.
 */

'use client';

export {
  LocaleSwitcher,
  LocaleSwitcherDialog,
  LocaleSwitcherDropdown,
  LocaleSwitcherTrigger,
  LocaleGrid,
  LocaleCard,
  getLocaleMeta,
} from './locale-switcher';
export type {
  LocaleSwitcherProps,
  LocaleSwitcherDialogProps,
  LocaleSwitcherDropdownProps,
  LocaleSwitcherTriggerProps,
  LocaleGridProps,
  LocaleCardProps,
  LocaleMeta,
  LocaleSwitcherBrand,
  LocaleSwitcherLabels,
  LocaleSwitcherSharedProps,
  LocaleSwitcherVariant,
} from './locale-switcher';

import { getLocaleMeta as _getLocaleMeta } from './locale-switcher';

/**
 * Native-name labels for common locales. Built from the central locale-meta
 * registry — kept as a `Record` for legacy callers that index it directly.
 */
export const LOCALE_LABELS: Record<string, string> = new Proxy(
  {} as Record<string, string>,
  {
    get(_target, prop: string) {
      if (typeof prop !== 'string') return undefined;
      return _getLocaleMeta(prop).native;
    },
  },
);
