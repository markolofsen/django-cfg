'use client';

/**
 * useSettingsSectionState — what a launcher of one Settings section needs to know: is the section registered with the
 * mounted dialog (a launcher for a missing section is a dead door), is the dialog showing it now, and how to open it.
 *
 * Reads the same store `useSettingsDialog` does. Registration comes from `<SettingsDialog />`, which lists its visible
 * sections (built-in and the host's) after it mounts, so before that, or with no dialog, nothing is registered.
 */

import { useCallback } from 'react';

import { useSettingsDialogStore } from '../store';

export interface SettingsSectionState {
  /** The dialog lists this section in its rail. */
  registered: boolean;
  /** The dialog is open and showing this section (an open dialog with no pick shows the first one). */
  active: boolean;
  /** Open the dialog on this section. */
  open: () => void;
}

export function useSettingsSectionState(id: string): SettingsSectionState {
  const registered = useSettingsDialogStore((s) => s.sections.some((section) => section.id === id));
  const active = useSettingsDialogStore(
    (s) => s.isOpen && (s.activeSection ?? s.sections[0]?.id ?? null) === id,
  );
  const storeOpen = useSettingsDialogStore((s) => s.open);
  const open = useCallback(() => storeOpen(id), [storeOpen, id]);
  return { registered, active, open };
}
