'use client';

import React, { useMemo, useState } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { Preloader } from '@djangocfg/ui-core/components';

import { SettingsShell } from './components';
import { SettingsProvider } from './context';
import { useSettingsCopy } from './i18n';
import { buildBuiltinSections, BUILTIN_GROUP, PLATFORM_GROUP } from './sections';
import type { SettingsFormProps, SettingsSection } from './types';

/**
 * SettingsForm — the inline (non-dialog) settings surface.
 *
 * Composition:
 *   SettingsProvider  (resolved sections, active selection, search)
 *     SettingsShell   (nav rail + detail panel)
 *
 * Built-in sections get their data/labels/save from `useProfileSave` directly
 * (no context wrapper) — see sections/useProfileSave.
 *
 * Selection is uncontrolled by default (local state); pass `activeSection` +
 * `onSectionChange` to control it (the dialog does this, bound to its store).
 * Built-in sections are merged ahead of app `sections`; ids must be unique.
 */
// Module constants: `= []` / `= {}` defaults are new objects every render and would defeat the memos below.
const NO_SECTIONS: NonNullable<SettingsFormProps['sections']> = [];
const NO_BUILTINS: NonNullable<SettingsFormProps['builtins']> = {};

export const SettingsForm: React.FC<SettingsFormProps> = ({
  title,
  sections: appSections = NO_SECTIONS,
  groups,
  builtins = NO_BUILTINS,
  generalRows,
  initialSection,
  searchable = 'auto',
  enableDeleteAccount = true,
  activeSection,
  onSectionChange,
  onUnauthenticated,
  className,
  bare = false,
}: SettingsFormProps) => {
  const t = useAppT();
  const copy = useSettingsCopy();
  const { user, isLoading } = useAuth();

  // Built-ins first, then app sections. Memoized so JSX identity is stable.
  const allSections = useMemo<SettingsSection[]>(() => {
    const builtin = buildBuiltinSections({ builtins, enableDeleteAccount, generalRows, copy });
    return [...builtin, ...appSections];
  }, [builtins, enableDeleteAccount, generalRows, appSections, copy]);

  // Ensure the built-in group exists/ordered even if the app passed its own groups.
  const allGroups = useMemo(() => {
    const provided = groups ?? [];
    const missing = [BUILTIN_GROUP, { ...PLATFORM_GROUP, label: copy.nav.platform }].filter(
      (b) => !provided.some((g) => g.id === b.id),
    );
    return [...missing, ...provided];
  }, [groups, copy]);

  // Uncontrolled selection fallback.
  const [localActive, setLocalActive] = useState<string | null>(initialSection ?? null);
  const isControlled = activeSection !== undefined;
  const resolvedActive = isControlled ? activeSection ?? null : localActive;
  const handleActiveChange = (id: string) => {
    if (!isControlled) setLocalActive(id);
    onSectionChange?.(id);
  };

  React.useEffect(() => {
    if (onUnauthenticated && !user && !isLoading) onUnauthenticated();
  }, [onUnauthenticated, user, isLoading]);

  if (isLoading) {
    return (
      <Preloader
        variant="fullscreen"
        text={t('ui.states.loading')}
        size="lg"
        backdrop
        backdropOpacity={80}
      />
    );
  }

  // Default to "Settings" — this surface is broader than the old Profile page.
  const resolvedTitle = title ?? copy.nav.title;

  return (
    <SettingsProvider
      title={resolvedTitle}
      sections={allSections}
      groups={allGroups}
      searchable={searchable}
      activeId={resolvedActive}
      onActiveChange={handleActiveChange}
      initialSection={initialSection}
    >
      <SettingsShell bare={bare} className={className} />
    </SettingsProvider>
  );
};
