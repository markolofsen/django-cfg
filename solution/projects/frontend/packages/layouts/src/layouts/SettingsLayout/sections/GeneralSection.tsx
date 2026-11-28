'use client';

import React from 'react';

import { SettingsBlock } from '@djangocfg/ui-core/components';

import { useSettingsCopy } from '../i18n';
import { PreferencesRows } from './PreferencesRows';

/**
 * Interface preferences — theme, language and time zone live here, not in the dialog
 * chrome. `children` are the host's own rows (see `SettingsContent.generalRows`),
 * rendered in a second block so they read as separate from the built-ins.
 */
export const GeneralSection: React.FC<React.PropsWithChildren> = ({ children }) => {
  const copy = useSettingsCopy();
  return (
  <div className="space-y-8">
    <SettingsBlock title={copy.prefs.general}>
      <PreferencesRows />
    </SettingsBlock>
    {children ? <SettingsBlock title={copy.prefs.other}>{children}</SettingsBlock> : null}
  </div>
  );
};
