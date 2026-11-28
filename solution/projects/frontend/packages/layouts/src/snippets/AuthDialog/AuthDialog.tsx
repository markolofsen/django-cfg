'use client';

import { LogIn } from 'lucide-react';
import React, { useMemo } from 'react';

import { useAuth, useCfgRouter } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import {
    Button, Dialog, DialogContent, DialogHeader, DialogTitle
} from '@djangocfg/ui-core/components';
import { useDialogStore } from '@djangocfg/ui-core/lib/dialog-service';

interface AuthDialogProps {
  onAuthRequired?: () => void;
  authPath?: string;
}

export const AuthDialog: React.FC<AuthDialogProps> = ({
  onAuthRequired,
  authPath
}) => {
  const open = useDialogStore((s) => s.authOpen);
  const authOptions = useDialogStore((s) => s.authOptions);
  const resolveAuth = useDialogStore((s) => s.resolveAuth);
  const t = useAppT();

  const labels = useMemo(() => ({
    authRequired: t('layouts.auth.authRequired'),
    pleaseSignIn: t('layouts.auth.pleaseSignIn'),
    goToSignIn: t('layouts.auth.goToSignIn'),
  }), [t]);

  const message = authOptions?.message || labels.pleaseSignIn;
  const router = useCfgRouter();
  const { saveRedirectUrl, routes } = useAuth();

  const handleClose = () => {
    resolveAuth(false);
  };

  const handleGoToAuth = () => {
    // Canonical post-login redirect persistence (the same store the guard and
    // verifyOTP read). The old private `redirectAfterAuth` sessionStorage key
    // was write-only — nothing ever read it.
    if (typeof window !== 'undefined') {
      saveRedirectUrl(authOptions?.redirectUrl || window.location.pathname);
    }

    if (onAuthRequired) {
      onAuthRequired();
    } else {
      router.push(authPath ?? routes.auth);
    }

    resolveAuth(true);
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => { if (!isOpen) handleClose(); }}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{labels.authRequired}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{message}</p>

          <Button onClick={handleGoToAuth} className="w-full">
            <LogIn className="h-4 w-4 mr-2" />
            {labels.goToSignIn}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
