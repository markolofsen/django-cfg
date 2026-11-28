'use client';

import React from 'react';

import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@djangocfg/ui-core/components';

import { TwoFactorSetup } from '../../../../snippets/TwoFactor';
import { useSettingsCopy } from '../../i18n';

export interface TwoFactorSetupDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Runs after the user dismisses the backup codes. */
  onComplete: () => void;
}

/**
 * Enabling 2FA is one focused task, so it gets its own dialog over Settings instead of
 * replacing the Security block inline. One exit (close); no "skip" — that belongs to the
 * sign-in flow, not to a deliberate opt-in. Content mounts only while open, so each
 * opening starts a fresh setup and an unfinished one is dropped on close.
 */
export const TwoFactorSetupDialog: React.FC<TwoFactorSetupDialogProps> = ({ open, onOpenChange, onComplete }) => {
  const copy = useSettingsCopy().security;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] w-[calc(100vw-1.5rem)] max-w-md flex-col items-center overflow-y-auto bg-card p-6">
        <DialogTitle className="sr-only">{copy.setupTitle}</DialogTitle>
        <DialogDescription className="sr-only">{copy.setupHint}</DialogDescription>
        {open && <TwoFactorSetup onComplete={onComplete} />}
      </DialogContent>
    </Dialog>
  );
};
