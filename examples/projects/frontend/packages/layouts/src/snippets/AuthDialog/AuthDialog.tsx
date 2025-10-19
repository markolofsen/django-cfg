'use client';

import { LogIn } from 'lucide-react';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import {
  Button,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@djangocfg/ui/components';
import { useEventListener } from '@djangocfg/ui/hooks';

// Re-export events for backwards compatibility
export const DIALOG_EVENTS = {
  OPEN_AUTH_DIALOG: 'OPEN_AUTH_DIALOG',
  CLOSE_AUTH_DIALOG: 'CLOSE_AUTH_DIALOG',
  AUTH_SUCCESS: 'AUTH_SUCCESS',
  AUTH_FAILURE: 'AUTH_FAILURE',
} as const;

interface AuthDialogProps {
  onAuthRequired?: () => void;
  authPath?: string;
}

export const AuthDialog: React.FC<AuthDialogProps> = ({
  onAuthRequired,
  authPath = '/auth'
}) => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState<string>('Please sign in to continue');
  const router = useRouter();

  // Listen for open auth dialog event
  useEventListener(DIALOG_EVENTS.OPEN_AUTH_DIALOG, (payload: any) => {
    if (payload?.message) {
      setMessage(payload.message);
    }
    setOpen(true);
  });

  // Listen for close auth dialog event
  useEventListener(DIALOG_EVENTS.CLOSE_AUTH_DIALOG, () => {
    setOpen(false);
  });

  const handleClose = () => {
    setMessage('Please sign in to continue');
    setOpen(false);
  };

  const handleGoToAuth = () => {
    // Save current URL for redirect after successful auth
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('redirectAfterAuth', window.location.pathname);
    }

    if (onAuthRequired) {
      onAuthRequired();
    } else {
      router.push(authPath);
    }

    handleClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Authentication Required</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{message}</p>

          <Button onClick={handleGoToAuth} className="w-full">
            <LogIn className="h-4 w-4 mr-2" />
            Go to Sign In
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
