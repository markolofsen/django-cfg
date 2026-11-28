'use client';

import React from 'react';
import { LogOut } from 'lucide-react';

import { useAuth } from '@djangocfg/api/auth';
import { Button, SettingRow, SettingsBlock } from '@djangocfg/ui-core/components';

import { AvatarSection } from '../components/AvatarSection';
import { useProfileSave } from '../hooks/useProfileSave';
import { TwoFactorSection } from '../components/TwoFactorSection';
import { useSettingsCopy } from '../i18n';
import { DeleteAccountRow } from './DeleteAccountRow';

interface AccountSectionProps {
  /** Render the "Danger zone" delete-account control. Default: true. */
  enableDeleteAccount?: boolean;
  /** Render the "Security" block (two-factor auth). Default: true. */
  enableSecurity?: boolean;
}

/**
 * Built-in "Account" section (profile + security + danger zone) — macOS / Claude-settings layout: flat blocks of
 * label↔control rows divided by hairlines, no card frames.
 *
 * Editable fields are declared inline via SettingRow's props API
 * (`value` + `editable` + `onSave`); the chip/input styling lives in SettingRow.
 * Save logic + labels come from `useProfileSave` (no context wrapper needed).
 */
export const AccountSection: React.FC<AccountSectionProps> = ({
  enableDeleteAccount = true,
  enableSecurity = true,
}) => {
  const copy = useSettingsCopy();
  const { labels, save: onFieldSave, logout } = useProfileSave();
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-7">
      {/* Avatar is the profile's identity header — centered above the fields,
          not a form row. */}
      <AvatarSection />

      <SettingsBlock title={labels.personalInfo}>
        <SettingRow
          label={labels.firstName}
          value={user.first_name || ''}
          placeholder={labels.addFirstName}
          editable
          onSave={(v) => onFieldSave('first_name', v)}
        />
        <SettingRow
          label={labels.lastName}
          value={user.last_name || ''}
          placeholder={labels.addLastName}
          editable
          onSave={(v) => onFieldSave('last_name', v)}
        />
        <SettingRow
          label={labels.phone}
          value={user.phone || ''}
          placeholder={labels.addPhone}
          type="phone"
          editable
          onSave={(v) => onFieldSave('phone', v)}
        />
      </SettingsBlock>

      <SettingsBlock title={labels.work}>
        <SettingRow
          label={labels.company}
          value={user.company || ''}
          placeholder={labels.addCompany}
          editable
          onSave={(v) => onFieldSave('company', v)}
        />
        <SettingRow
          label={labels.position}
          value={user.position || ''}
          placeholder={labels.addPosition}
          editable
          onSave={(v) => onFieldSave('position', v)}
        />
      </SettingsBlock>

      {enableSecurity && <TwoFactorSection />}

      <SettingsBlock title={labels.actions}>
        <SettingRow
          label={labels.signOut}
          action={
            <Button
              variant="outline"
              size="sm"
              onClick={logout}
              className="shrink-0 border-destructive/40 text-destructive hover:bg-destructive/10 hover:text-destructive"
            >
              <LogOut className="size-4" />
              {labels.signOut}
            </Button>
          }
        />
      </SettingsBlock>

      {enableDeleteAccount && (
        // The whole Danger zone is collapsible (closed by default) so
        // destructive actions stay tucked away until deliberately revealed.
        <SettingsBlock title={copy.account.dangerZone} collapsible defaultOpen={false}>
          <DeleteAccountRow />
        </SettingsBlock>
      )}
    </div>
  );
};
