'use client';

import { useCallback } from 'react';

import { useSettingsDialogStore } from '../store';

export interface SettingsIntent {
  /** The section the link named, when it named a known one. */
  section: string | null;
  params: Record<string, string>;
}

/**
 * What the address asked of this section (`#settings/<section>?…`), or null when it asked nothing. The dialog sets it
 * once from the fragment and strips the query; it stays until the section calls `clear` or the dialog closes, so a
 * section that mounts a moment later still sees it.
 */
export function useSettingsIntent(sectionId: string): { params: Record<string, string>; clear: () => void } | null {
  const intent = useSettingsDialogStore((s) => s.intent);
  const clearIntent = useSettingsDialogStore((s) => s.clearIntent);
  const clear = useCallback(() => clearIntent(), [clearIntent]);
  return intent && intent.section === sectionId ? { params: intent.params, clear } : null;
}
