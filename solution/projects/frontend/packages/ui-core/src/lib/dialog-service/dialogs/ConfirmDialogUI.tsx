'use client';

import { useMemo } from 'react';
import { useT } from '@djangocfg/i18n';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../../../components/overlay/alert-dialog';
import { buttonVariants } from '../../../components/forms/button';
import { useHotkey } from '../../../hooks';
import { cn } from '../../utils';
import { I18N_KEYS } from '../constants';
import type { DialogOptions } from '../types';

interface ConfirmDialogUIProps {
  open: boolean;
  options: DialogOptions;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialogUI({
  open,
  options,
  onConfirm,
  onCancel,
}: ConfirmDialogUIProps) {
  const t = useT();

  // Prepare data before render
  const dialogData = useMemo(() => {
    const isDestructive = options.variant === 'destructive';
    return {
      title: options.title || t(I18N_KEYS.confirmTitle),
      message: options.message,
      confirmText: options.confirmText || t(I18N_KEYS.confirm),
      cancelText: options.cancelText || t(I18N_KEYS.cancel),
      preventClose: options.preventClose ?? false,
      isDestructive,
      confirmClassName: cn(isDestructive && buttonVariants({ variant: 'destructive' })),
    };
  }, [options, t]);

  // Hotkey: Enter to confirm, Escape to cancel
  useHotkey('enter', onConfirm, { enabled: open, preventDefault: true });
  useHotkey('escape', onCancel, { enabled: open });

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen && !dialogData.preventClose) {
      onCancel();
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
          <AlertDialogCancel onClick={onCancel}>
            {dialogData.cancelText}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className={dialogData.confirmClassName}
            autoFocus
          >
            {dialogData.confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
