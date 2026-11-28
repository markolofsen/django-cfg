'use client';

import React from 'react';

import { Bug, KeyRound, Settings as SettingsIcon, UserRound } from 'lucide-react';

import type { SettingsBuiltins, SettingsGroup, SettingsSection } from '../types';
import { AccountSection } from './AccountSection';
import { GeneralSection } from './GeneralSection';
import { ApiKeysSection } from './ApiKeysSection';
import { DebugSection } from './DebugSection';
import type { SettingsCopy } from '../i18n';

/**
 * The (unlabelled) group Account and Preferences belong to — they open the rail, like Claude. App sections can reuse this id
 * to sit alongside the built-ins, or define their own groups.
 */
export const BUILTIN_GROUP: SettingsGroup = { id: 'general', order: 0 };

/** Developer-facing sections (API keys). */
export const PLATFORM_GROUP: SettingsGroup = { id: 'platform', order: 1 };

interface BuildBuiltinArgs {
  builtins: SettingsBuiltins;
  enableDeleteAccount: boolean;
  generalRows?: React.ReactNode;
  copy: SettingsCopy;
}

/**
 * Construct the enabled built-in sections. Pure function of the flags and the
 * active `copy` — nav-level labels/titles come from the Settings dictionaries.
 *
 * Defaults: everything on. Security (2FA) is a block inside Account, not its own
 * section — `/cfg/totp/*` ships with every django-cfg backend. Apps that truly
 * lack it opt out explicitly via `builtins.security: false`.
 */
export function buildBuiltinSections({
  builtins,
  enableDeleteAccount,
  generalRows,
  copy,
}: BuildBuiltinArgs): SettingsSection[] {
  const { general = true, account = true, security = true, apiKeys = true, debug = false } = builtins;
  const sections: SettingsSection[] = [];

  if (account) {
    sections.push({
      id: 'account',
      label: copy.nav.account,
      icon: UserRound,
      group: BUILTIN_GROUP.id,
      title: copy.nav.account,
      keywords: ['profile', 'name', 'email', 'avatar', 'security', '2fa', 'two-factor', 'mfa', 'authenticator'],
      content: <AccountSection enableDeleteAccount={enableDeleteAccount} enableSecurity={security} />,
    });
  }

  if (general) {
    sections.push({
      id: 'general',
      label: copy.nav.preferences,
      icon: SettingsIcon,
      group: BUILTIN_GROUP.id,
      title: copy.nav.preferences,
      keywords: ['theme', 'appearance', 'dark', 'light', 'language', 'locale', 'preferences'],
      content: <GeneralSection>{generalRows}</GeneralSection>,
    });
  }

  if (apiKeys) {
    sections.push({
      id: 'api-keys',
      label: copy.nav.apiKeys,
      icon: KeyRound,
      group: PLATFORM_GROUP.id,
      title: copy.nav.apiKeys,
      description: copy.nav.apiKeysDescription,
      keywords: ['api', 'token', 'key', 'secret', 'developer'],
      content: <ApiKeysSection />,
    });
  }

  if (debug) {
    sections.push({
      id: 'debug',
      label: copy.nav.debug,
      icon: Bug,
      group: PLATFORM_GROUP.id,
      title: copy.nav.debug,
      description: copy.debug.description,
      keywords: ['viewport', 'scroll', 'hud', 'diagnostics'],
      content: <DebugSection />,
    });
  }

  return sections;
}
