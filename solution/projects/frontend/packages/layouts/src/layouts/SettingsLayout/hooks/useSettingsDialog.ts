'use client';

/**
 * useSettingsDialog — the public API external consumers use to drive the
 * globally-mounted <SettingsDialog />.
 *
 * @example
 *   const settings = useSettingsDialog();
 *   <Button onClick={() => settings.open()}>Settings</Button>
 *   <MenuItem onClick={() => settings.open('billing')}>Billing</MenuItem>
 *
 * The id is `string` by default. Pass the union of your sections to make a typo a compile error:
 *   const settings = useSettingsDialog<SettingsSectionId<typeof sections>>();   // see `defineSettingsSections`
 *
 * Returns stable callbacks, safe in deps arrays. The dialog itself must be
 * mounted once in the tree (PrivateLayout does this).
 */

import { useCallback, useMemo } from 'react';

import { useSettingsDialogStore, type SettingsMenuSection } from '../store';

export interface UseSettingsDialogReturn<Id extends string = string> {
  /** Whether the dialog is currently open. */
  isOpen: boolean;
  /** Currently active section id (null = fall back to first). */
  activeSection: Id | null;
  /** Open the dialog, optionally on a specific section. */
  open: (sectionId?: Id) => void;
  /** Close the dialog. */
  close: () => void;
  /** Toggle open/closed. */
  toggle: () => void;
  /** Switch the active section. */
  setSection: (sectionId: Id) => void;
  /** The visible sections of the mounted dialog (built-in and the host's), in rail order: for menu shortcuts, `open(id)`. */
  sections: SettingsMenuSection[];
}

export function useSettingsDialog<Id extends string = string>(): UseSettingsDialogReturn<Id> {
  const isOpen = useSettingsDialogStore((s) => s.isOpen);
  const activeSection = useSettingsDialogStore((s) => s.activeSection);
  const storeOpen = useSettingsDialogStore((s) => s.open);
  const storeClose = useSettingsDialogStore((s) => s.close);
  const storeToggle = useSettingsDialogStore((s) => s.toggle);
  const storeSetSection = useSettingsDialogStore((s) => s.setSection);
  const sections = useSettingsDialogStore((s) => s.sections);

  const open = useCallback((sectionId?: Id) => storeOpen(sectionId), [storeOpen]);
  const close = useCallback(() => storeClose(), [storeClose]);
  const toggle = useCallback(() => storeToggle(), [storeToggle]);
  const setSection = useCallback((id: Id) => storeSetSection(id), [storeSetSection]);

  return useMemo(
    () => ({ isOpen, activeSection: activeSection as Id | null, open, close, toggle, setSection, sections }),
    [isOpen, activeSection, open, close, toggle, setSection, sections],
  );
}
