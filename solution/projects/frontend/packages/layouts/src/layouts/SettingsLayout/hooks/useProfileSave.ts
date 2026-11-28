'use client';

/**
 * useProfileSave — the account-section data layer, as a plain hook (no context).
 *
 * Replaces the old ProfileProvider/useProfileContext plumbing: the labels are
 * just i18n, `save` wraps `updateProfile` + toast, and `logout` is the shared
 * logout hook. Every value here is already reachable via global hooks, so a
 * React context added nothing but a wrapper — sections call this directly.
 */

import { useCallback, useMemo } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { toast } from '@djangocfg/ui-core/hooks';

import { profileLogger } from '../../../utils/logger';
import { useLogout } from '../../../hooks';

export interface ProfileLabels {
  title: string;
  personalInfo: string;
  work: string;
  preferences: string;
  actions: string;
  signOut: string;
  firstName: string;
  lastName: string;
  phone: string;
  company: string;
  position: string;
  addFirstName: string;
  addLastName: string;
  addPhone: string;
  addCompany: string;
  addPosition: string;
  deleteAccount: string;
  profileUpdated: string;
  failedToUpdate: string;
  loading: string;
}

export interface UseProfileSaveReturn {
  labels: ProfileLabels;
  /** Persist a single profile field; shows a toast on success/error. */
  save: (field: string, value: string) => Promise<void>;
  /** Sign the user out. */
  logout: () => void;
}

export function useProfileSave(title?: string): UseProfileSaveReturn {
  const { updateProfile } = useAuth();
  const t = useAppT();
  const logout = useLogout();

  const labels = useMemo<ProfileLabels>(
    () => ({
      title: title || t('layouts.profilePage.title'),
      personalInfo: t('layouts.profilePage.personalInfo'),
      work: t('layouts.profilePage.work'),
      preferences: 'Preferences',
      actions: t('layouts.profilePage.actions'),
      signOut: t('layouts.profilePage.signOut'),
      firstName: t('layouts.profilePage.firstName'),
      lastName: t('layouts.profilePage.lastName'),
      phone: t('layouts.profilePage.phone'),
      company: t('layouts.profilePage.company'),
      position: t('layouts.profilePage.position'),
      addFirstName: t('layouts.profilePage.addFirstName') || 'Add first name',
      addLastName: t('layouts.profilePage.addLastName') || 'Add last name',
      addPhone: t('layouts.profilePage.addPhone') || 'Add phone number',
      addCompany: t('layouts.profilePage.addCompany') || 'Add company',
      addPosition: t('layouts.profilePage.addPosition') || 'Add position',
      deleteAccount: t('layouts.profilePage.deleteAccount'),
      profileUpdated: t('layouts.profilePage.profileUpdated'),
      failedToUpdate: t('layouts.profilePage.failedToUpdate'),
      loading: t('ui.states.loading'),
    }),
    [t, title],
  );

  const save = useCallback(
    async (field: string, value: string) => {
      try {
        await updateProfile({ [field]: value });
        toast.success(labels.profileUpdated);
      } catch (error: unknown) {
        profileLogger.error('Profile update error:', error);
        const apiErr = error as { response?: Record<string, string[]> };
        toast.error(apiErr?.response?.[field]?.[0] || labels.failedToUpdate);
        throw error;
      }
    },
    [updateProfile, labels],
  );

  return { labels, save, logout };
}
