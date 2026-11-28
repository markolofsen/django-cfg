'use client';

/**
 * SettingsDialog store.
 *
 * Holds only transient dialog state: whether it's open and which section is
 * active. Section *definitions* are NOT stored here — they're passed as props
 * to `<SettingsDialog />` so they can include live JSX/handlers from the host
 * app. Consumers open the dialog imperatively via `useSettingsDialog()` or
 * declaratively via the URL hash (see `useSettingsUrl`).
 *
 * Mirrors the established `useProfileDialogStore` pattern so both dialogs feel
 * identical to wire up. ProfileLayout's store stays separate and untouched.
 */

import { create } from 'zustand';

import type { SettingsIntent } from './intent/useSettingsIntent';

/** What a menu needs to link to a section; the dialog registers these (host sections are only known to it). */
export interface SettingsMenuSection {
  id: string;
  label: React.ReactNode;
  icon?: React.ComponentType<{ className?: string }>;
}

interface SettingsDialogState {
  /** The visible sections of the mounted dialog, in rail order, for menu shortcuts. */
  sections: SettingsMenuSection[];
  setSections: (sections: SettingsMenuSection[]) => void;
  /** Whether the dialog is visible. */
  isOpen: boolean;
  /**
   * Active section id, or null to mean "fall back to the first section".
   * Kept separate from isOpen so a deep-link can preset the section before open.
   */
  activeSection: string | null;
  /** Open the dialog, optionally on a specific section. */
  open: (sectionId?: string) => void;
  /** Close the dialog. Leaves activeSection as-is (cheap to reopen same spot). */
  close: () => void;
  /** Toggle visibility. */
  toggle: () => void;
  /** Switch the active section (no-op on open state). */
  setSection: (sectionId: string) => void;
  /** One-shot parameters from the address (`#settings/<section>?…`), read by the section they name. */
  intent: SettingsIntent | null;
  setIntent: (intent: SettingsIntent) => void;
  clearIntent: () => void;
}

/**
 * Same shortcuts, whatever the identity of the array or of the host's JSX labels. The dialog re-registers on
 * every render of a host that passes `sections` inline; storing a fresh array each time would re-render every
 * menu that reads `sections`, and when that menu shares a parent with the dialog the two feed each other.
 * String labels are compared by value; a node label is trusted to follow its id.
 */
function sameMenuSections(a: SettingsMenuSection[], b: SettingsMenuSection[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((x, i) => {
    const y = b[i]!;
    const sameLabel = typeof x.label === 'string' || typeof y.label === 'string' ? x.label === y.label : true;
    return x.id === y.id && x.icon === y.icon && sameLabel;
  });
}

export const useSettingsDialogStore = create<SettingsDialogState>((set, get) => ({
  sections: [],
  setSections: (sections) => {
    if (sameMenuSections(get().sections, sections)) return;
    set({ sections });
  },
  isOpen: false,
  activeSection: null,
  open: (sectionId) =>
    set((state) => ({
      isOpen: true,
      activeSection: sectionId ?? state.activeSection,
    })),
  /* Closing drops an unanswered intent: reopening later must not replay a stale request. */
  close: () => set({ isOpen: false, intent: null }),
  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
  setSection: (sectionId) => set({ activeSection: sectionId }),
  intent: null,
  setIntent: (intent) => set({ intent }),
  clearIntent: () => set({ intent: null }),
}));
