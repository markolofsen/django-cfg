'use client';

import { Languages, LogOut, Settings as SettingsIcon } from 'lucide-react';
import { useMemo, type ReactNode } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { LanguageFlag } from '@djangocfg/ui-core/components';
import type { MenuItem } from '@djangocfg/ui-core/components';

import { useLogout } from '../../hooks';
import { getLocaleMeta } from '../../layouts/_components/locale-switcher/localeMeta';
import { useSettingsDialogStore } from '../../layouts/SettingsLayout/store';
import { useLayoutI18nOptional } from '../../shared/LayoutI18nProvider';
import type { UserMenuGroup, UserMenuLocaleConfig } from '../../layouts/types';

export interface UseAccountMenuItemsOptions {
  /** Items placed after the language submenu, before Sign out (app links). */
  extra?: MenuItem[];
  /** App link groups (`UserMenuConfig.groups`): each becomes a section, between the Settings rows and Language. */
  groups?: UserMenuGroup[];
  /** Label above the items; defaults to the signed-in user's email. Any node (a name + email block). */
  label?: ReactNode | null;
  /** Language submenu, shown when there is more than one locale. @default true */
  language?: boolean;
  /** Locales to offer; defaults to the layout i18n context (`BaseApp` `i18n`). */
  i18n?: UserMenuLocaleConfig;
  /** One row per Settings section (needs a mounted Settings dialog). Off for sites without it. @default true */
  settings?: boolean;
}

/** `UserMenuConfig.groups` as menu sections (an item may be a link or a handler). */
export function groupsToMenuItems(groups: UserMenuGroup[] | undefined): MenuItem[] {
  return (groups ?? []).map((group, i): MenuItem => ({
    kind: 'section',
    id: `group-${i}`,
    label: group.title,
    items: group.items.map((item, j): MenuItem => ({
      kind: 'item',
      id: item.href ?? `${i}-${j}`,
      label: item.label,
      icon: item.icon,
      href: item.href,
      onSelect: item.onClick ? () => item.onClick!() : undefined,
      variant: item.variant === 'destructive' ? 'destructive' : 'default',
    })),
  }));
}

/**
 * The ONE account menu content every host shares (public navbar, private bar avatar, sidebar footer): identity label,
 * a row per Settings section, the app's link groups, a Language submenu, then Sign out. Feed it to `MenuBuilder` with
 * any trigger (`AccountMenu` does that).
 */
export function useAccountMenuItems({ extra, groups, label, language = true, i18n, settings = true }: UseAccountMenuItemsOptions = {}): MenuItem[] {
  const { user } = useAuth();
  const t = useAppT();
  const handleLogout = useLogout();
  const contextI18n = useLayoutI18nOptional();
  const layoutI18n = i18n ?? contextI18n;
  const sections = useSettingsDialogStore((s) => s.sections);
  const headerLabel = label === undefined ? (user?.email ?? null) : label;
  const signOutLabel = t('layouts.profile.signOut');
  const settingsLabel = t('layouts.profile.settings') || 'Settings';
  const languageLabel = t('layouts.profile.language') || 'Language';

  return useMemo<MenuItem[]>(() => {
    const items: MenuItem[] = [];
    if (headerLabel) items.push({ kind: 'label', id: 'email', label: headerLabel });

    // The menu mirrors the dialog's sidebar (same sections, order and icons) instead of adding a generic
    // "Settings" row that opens the same first section. With no sections at all one "Settings" row stays.
    if (settings && sections.length === 0) {
      items.push({
        kind: 'item',
        id: 'settings',
        label: settingsLabel,
        icon: SettingsIcon,
        onSelect: () => useSettingsDialogStore.getState().open(),
      });
    }
    (settings ? sections : []).forEach((section) => {
      items.push({
        kind: 'item',
        id: `settings-${section.id}`,
        label: section.label,
        icon: section.icon,
        onSelect: () => useSettingsDialogStore.getState().open(section.id),
      });
    });

    items.push(...groupsToMenuItems(groups));

    if (language && layoutI18n && layoutI18n.locales.length > 1) {
      items.push({
        kind: 'submenu',
        id: 'language',
        label: languageLabel,
        icon: Languages,
        items: [
          {
            kind: 'radio-group',
            id: 'locale',
            value: layoutI18n.locale,
            onValueChange: layoutI18n.onLocaleChange,
            options: layoutI18n.locales.map((code) => ({
              id: code,
              value: code,
              label: getLocaleMeta(code).native,
              icon: <LanguageFlag code={code} rounded className="h-3 w-4 shrink-0" />,
            })),
          },
        ],
      });
    }

    if (extra?.length) items.push(...extra);

    items.push({ kind: 'separator', id: 'sep-logout' });
    items.push({
      kind: 'item',
      id: 'logout',
      label: signOutLabel,
      icon: LogOut,
      variant: 'destructive',
      onSelect: () => handleLogout(),
    });
    return items;
  }, [headerLabel, settingsLabel, languageLabel, language, settings, groups, layoutI18n, sections, extra, signOutLabel, handleLogout]);
}
