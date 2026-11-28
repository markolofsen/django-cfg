'use client';

import { useEffect, useCallback, type ReactNode } from 'react';
import { AlertDialogUI, ConfirmDialogUI, PromptDialogUI } from './dialogs';
import { initDialogAPI, useDialogStore } from './store';

interface DialogProviderProps {
  children: ReactNode;
}

/**
 * DialogProvider - Reads from zustand dialog store and renders appropriate dialogs
 *
 * Must be mounted once at the app root (e.g., in BaseApp).
 * Handles dialog queue to show one dialog at a time.
 */
export function DialogProvider({ children }: DialogProviderProps) {
  const current = useDialogStore((s) => s.current);
  const resolve = useDialogStore((s) => s.resolve);

  // Initialize global window.dialog API on mount
  useEffect(() => {
    initDialogAPI();
  }, []);

  // Handle dialog close
  const handleClose = useCallback(
    (result: boolean | string | null) => {
      resolve(result);
    },
    [resolve],
  );

  // Render current dialog
  const renderDialog = () => {
    if (!current) return null;

    switch (current.type) {
      case 'alert':
        return (
          <AlertDialogUI
            open={true}
            options={current.options}
            onClose={() => handleClose(true)}
          />
        );
      case 'confirm':
        return (
          <ConfirmDialogUI
            open={true}
            options={current.options}
            onConfirm={() => handleClose(true)}
            onCancel={() => handleClose(false)}
          />
        );
      case 'prompt':
        return (
          <PromptDialogUI
            open={true}
            options={current.options}
            onConfirm={(value) => handleClose(value)}
            onCancel={() => handleClose(null)}
          />
        );
      default:
        return null;
    }
  };

  return (
    <>
      {children}
      {renderDialog()}
    </>
  );
}
