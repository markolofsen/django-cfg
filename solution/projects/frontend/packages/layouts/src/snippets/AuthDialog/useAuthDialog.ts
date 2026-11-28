'use client';

import { useCallback } from 'react';
import { dialogStore } from '@djangocfg/ui-core/lib/dialog-service';
import type { AuthDialogOptions } from '@djangocfg/ui-core/lib/dialog-service';

/**
 * Hook to control auth dialog from anywhere in the app
 *
 * @example
 * ```tsx
 * const { openAuthDialog, closeAuthDialog } = useAuthDialog();
 *
 * // Opens auth dialog and waits for result
 * const didAuth = await openAuthDialog({ message: 'Session expired' });
 *
 * // Or fire-and-forget
 * openAuthDialog();
 * ```
 */
export function useAuthDialog() {
  const openAuthDialog = useCallback((options?: AuthDialogOptions) => {
    return dialogStore.getState().openAuth(options);
  }, []);

  const closeAuthDialog = useCallback(() => {
    dialogStore.getState().resolveAuth(false);
  }, []);

  return {
    openAuthDialog,
    closeAuthDialog,
  };
}
