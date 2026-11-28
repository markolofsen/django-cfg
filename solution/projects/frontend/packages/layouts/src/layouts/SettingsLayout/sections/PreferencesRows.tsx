'use client';

import React from 'react';

import { useTimezone } from '@djangocfg/api/auth';
import { SettingRow, TimezoneSelect } from '@djangocfg/ui-core/components';
import { ThemeSegmented } from '@djangocfg/ui-core/theme';

import { LocaleSwitcherDropdown } from '../../_components/locale-switcher';
import { useSettingsCopy } from '../i18n';
import { useLayoutI18nOptional } from '../../../shared/LayoutI18nProvider';

/**
 * Preferences as native SettingRows (Language + Time zone + Theme), so they share the exact
 * row/divider/spacing of the rest of the settings panel. Mirrors the controls
 * from ProfileLayout's PreferencesSection but in the lighter Claude-style row
 * layout. Language only renders when a layout i18n context is present.
 */
export const PreferencesRows: React.FC = () => {
  const copy = useSettingsCopy();
  const layoutI18n = useLayoutI18nOptional();
  const { preference, setTimezone } = useTimezone();

  return (
    <>
      {layoutI18n && (
        <SettingRow
          label={copy.prefs.language}
          action={
            <LocaleSwitcherDropdown
              locale={layoutI18n.locale}
              locales={layoutI18n.locales}
              onChange={layoutI18n.onLocaleChange}
              variant="outline"
              size="sm"
              showCode
              showIcon={false}
              showFlag
              showTriggerLabel
            />
          }
        />
      )}
      <SettingRow
        label={copy.prefs.timeZone}
        action={<TimezoneSelect value={preference} onChange={setTimezone} className="w-72" />}
      />
      <SettingRow label={copy.prefs.theme} action={<ThemeSegmented />} />
    </>
  );
};
