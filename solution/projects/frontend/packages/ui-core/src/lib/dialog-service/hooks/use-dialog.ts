'use client';

import { useCallback } from 'react';
import { showDialog, dialogStore } from '../store';
import type { DialogOptions, AuthDialogOptions } from '../types';

/**
 * React hook for using dialog service
 *
 * Provides type-safe access to dialogs via zustand store with fallback to native dialogs.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { confirm, alert, prompt, auth } = useDialog();
 *
 *   const handleDelete = async () => {
 *     const confirmed = await confirm({
 *       title: 'Delete Item',
 *       message: 'Are you sure?',
 *       variant: 'destructive',
 *     });
 *     if (confirmed) {
 *       // delete logic
 *     }
 *   };
 *
 *   const handleProtected = async () => {
 *     const authed = await auth({ message: 'Please sign in to continue' });
 *     if (authed) {
 *       // proceed
 *     }
 *   };
 *
 *   return <button onClick={handleDelete}>Delete</button>;
 * }
 * ```
 */
export function useDialog() {
  const alert = useCallback(
    (message: string | DialogOptions): Promise<void> => {
      if (typeof window === 'undefined') {
        return Promise.resolve();
      }
      if (!window.dialog) {
        window.alert(typeof message === 'string' ? message : message.message);
        return Promise.resolve();
      }
      return showDialog('alert', message).then(() => undefined);
    },
    [],
  );

  const confirm = useCallback(
    (message: string | DialogOptions): Promise<boolean> => {
      if (typeof window === 'undefined') {
        return Promise.resolve(false);
      }
      if (!window.dialog) {
        return Promise.resolve(
          window.confirm(typeof message === 'string' ? message : message.message),
        );
      }
      return showDialog('confirm', message) as Promise<boolean>;
    },
    [],
  );

  const prompt = useCallback(
    (message: string | DialogOptions): Promise<string | null> => {
      if (typeof window === 'undefined') {
        return Promise.resolve(null);
      }
      if (!window.dialog) {
        const opts = typeof message === 'string' ? { message } : message;
        return Promise.resolve(window.prompt(opts.message, opts.defaultValue));
      }
      return showDialog('prompt', message) as Promise<string | null>;
    },
    [],
  );

  const auth = useCallback(
    (options?: AuthDialogOptions): Promise<boolean> => {
      return dialogStore.getState().openAuth(options);
    },
    [],
  );

  return { alert, confirm, prompt, auth };
}
