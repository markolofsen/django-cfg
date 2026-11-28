/**
 * LocaleSwitcher Component (Smart)
 *
 * Wrapper around `@djangocfg/layouts` LocaleSwitcher with next-intl plumbing.
 * Mounts its own `LayoutI18nProvider` so the switcher works standalone — no
 * need to wrap the page in `<AppLayout i18n={...}>` just to render it.
 *
 * @example
 * ```tsx
 * import { LocaleSwitcher } from '@djangocfg/nextjs/i18n/components';
 *
 * <LocaleSwitcher />
 * <LocaleSwitcher locales={['en', 'ru']} />
 * <LocaleSwitcher labels={{ en: 'English', ru: 'Русский' }} />
 * ```
 */

'use client';

import {
  LayoutI18nProvider,
  LocaleSwitcher as BaseLocaleSwitcher,
  type LocaleSwitcherProps as BaseLocaleSwitcherProps,
} from '@djangocfg/layouts';

import { useLocaleSwitcher } from '../client';
import type { LocaleCode } from '../types';

export interface LocaleSwitcherProps extends BaseLocaleSwitcherProps {
  /** Available locales (defaults to all from routing config) */
  locales?: LocaleCode[];
}

export function LocaleSwitcher({ locales: customLocales, ...props }: LocaleSwitcherProps) {
  const { locale, locales: routingLocales, changeLocale } = useLocaleSwitcher();

  const availableLocales = customLocales || routingLocales;

  return (
    <LayoutI18nProvider
      value={{
        locale,
        locales: availableLocales,
        onLocaleChange: changeLocale,
      }}
    >
      <BaseLocaleSwitcher {...props} />
    </LayoutI18nProvider>
  );
}
