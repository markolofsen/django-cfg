'use client';

import React from 'react';
import { Loader2, Trash2 } from 'lucide-react';

import { useDeleteAccount } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { Button, SettingRow } from '@djangocfg/ui-core/components';

import { useSettingsCopy } from '../i18n';

/**
 * Compact "Delete account" row — a flat row with a small destructive button on
 * the right. Lives inside the collapsible "Danger zone" block, so the section
 * itself is what's hidden by default; the typed-confirmation prompt is the
 * final safety gate.
 */
export const DeleteAccountRow: React.FC = () => {
  const { deleteAccount, isLoading } = useDeleteAccount();
  const t = useAppT();
  const copy = useSettingsCopy();

  const confirmationWord = t('layouts.profilePage.confirmationWord');

  const handleDelete = async () => {
    const value = await window.dialog.prompt({
      title: t('layouts.profilePage.deleteAccountTitle'),
      message: t('layouts.profilePage.deleteAccountDesc'),
      placeholder: confirmationWord,
      confirmText: t('layouts.profilePage.deleteAccount'),
      cancelText: t('layouts.profilePage.cancel'),
      variant: 'destructive',
    });

    if (value?.toUpperCase() !== confirmationWord.toUpperCase()) return;

    await deleteAccount();
  };

  return (
    <SettingRow
      label={t('layouts.profilePage.deleteAccount')}
      description={copy.account.deleteAccountDescription}
      action={
        <Button
          variant="destructive"
          size="sm"
          onClick={handleDelete}
          disabled={isLoading}
          className="shrink-0"
        >
          {isLoading ? <Loader2 className="size-4 animate-spin" /> : <Trash2 className="size-4" />}
          {t('layouts.profilePage.deleteAccount')}
        </Button>
      }
    />
  );
};
