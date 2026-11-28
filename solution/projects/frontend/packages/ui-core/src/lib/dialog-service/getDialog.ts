'use client';

import type { DialogAPI } from './types';

/**
 * Lazy accessor for the global `window.dialog` API installed by
 * `<DialogProvider />`. Use this in any library code that needs to call
 * `dialog.confirm` / `dialog.alert` / `dialog.prompt` from a non-React
 * context (e.g. event handlers in `ui-tools` tools).
 *
 * Returns `null` (and warns once in dev) when:
 *   - we're rendering on the server (`typeof window === 'undefined'`)
 *   - the host app has not mounted `<DialogProvider />`, so `window.dialog`
 *     is missing.
 *
 * The caller must handle the `null` case — usually by bailing out of the
 * action with a console warning. Library code must never throw if the
 * provider is missing; consumers without it should still be able to
 * import / render the component (just without CRUD flows).
 *
 * @example
 * const dialog = getDialog();
 * if (!dialog) return;
 * const ok = await dialog.confirm({ title: 'Delete?', message: '…', variant: 'destructive' });
 * if (ok) await onDelete();
 */
export function getDialog(): DialogAPI | null {
  if (typeof window === 'undefined') return null;
  const api = (window as Window & { dialog?: DialogAPI }).dialog;
  if (!api) {
    if (process.env.NODE_ENV !== 'production' && !warnedMissing) {
      warnedMissing = true;
       
      console.warn(
        '[getDialog] window.dialog is not available — mount <DialogProvider /> at the app root.',
      );
    }
    return null;
  }
  return api;
}

let warnedMissing = false;

/**
 * Like `getDialog()` but throws when unavailable. Use sparingly — only in
 * code paths where missing `window.dialog` is a developer error (e.g. an
 * action explicitly triggered by user interaction in a feature that
 * unconditionally requires dialogs).
 */
export function requireDialog(): DialogAPI {
  const api = getDialog();
  if (!api) {
    throw new Error(
      'requireDialog(): window.dialog is not available. Mount <DialogProvider /> at the app root.',
    );
  }
  return api;
}
