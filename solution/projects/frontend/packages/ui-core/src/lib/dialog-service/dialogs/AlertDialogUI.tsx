'use client';

import { useMemo } from 'react';
import { useT } from '@djangocfg/i18n';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../../../components/overlay/alert-dialog';
import { useHotkey } from '../../../hooks';
import { I18N_KEYS } from '../constants';
import type { DialogOptions } from '../types';

interface AlertDialogUIProps {
  open: boolean;
  options: DialogOptions;
  onClose: () => void;
}

export function AlertDialogUI({ open, options, onClose }: AlertDialogUIProps) {
  const t = useT();

  // Prepare data before render
  const dialogData = useMemo(() => ({
    title: options.title || t(I18N_KEYS.alertTitle),
    message: options.message,
    confirmText: options.confirmText || t(I18N_KEYS.ok),
    preventClose: options.preventClose ?? false,
  }), [options, t]);

  // Hotkey: Enter to confirm
  useHotkey('enter', onClose, { enabled: open, preventDefault: true });

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen && !dialogData.preventClose) {
      onClose();
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{dialogData.title}</AlertDialogTitle>
          <AlertDialogDescription>{dialogData.message}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction onClick={onClose}>
            {dialogData.confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
