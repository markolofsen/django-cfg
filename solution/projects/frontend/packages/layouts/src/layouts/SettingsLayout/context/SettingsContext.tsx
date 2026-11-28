'use client';

/**
 * SettingsContext — the resolved runtime state shared by the shell parts
 * (nav rail, search box, detail panel). Holds the derived section structure,
 * the active section, and the search query. Selection can be driven by the
 * zustand store (dialog mode) or local state (inline mode); the provider
 * abstracts that difference so child components never care which.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';

import { useSettingsSections } from '../hooks/useSettingsSections';
import type { ResolvedGroup } from '../hooks/useSettingsSections';
import type { SettingsGroup, SettingsSection } from '../types';

interface SettingsContextValue {
  /** Title for the surface header. */
  title: React.ReactNode;
  /** Groups (with sections) after ordering + search filtering. */
  groups: ResolvedGroup[];
  /** Flat visible sections in render order. */
  visible: SettingsSection[];
  /** The currently active section object (or null if none resolvable). */
  active: SettingsSection | null;
  /** Active section id. */
  activeId: string | null;
  /** Switch active section. */
  setActive: (id: string) => void;
  /** Search query + setter. */
  query: string;
  setQuery: (q: string) => void;
  /** Whether the search box should render. */
  searchable: boolean;
}

/** `searchable: 'auto'` shows the search box only when the rail is long enough to need it. */
export const SEARCH_MIN_SECTIONS = 10;

const SettingsContext = createContext<SettingsContextValue | null>(null);

export const useSettingsContext = (): SettingsContextValue => {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettingsContext must be used within SettingsProvider');
  return ctx;
};

export interface SettingsProviderProps {
  children: React.ReactNode;
  title: React.ReactNode;
  /** Fully-merged sections (built-ins + app), pre-concatenated by the caller. */
  sections: SettingsSection[];
  groups?: SettingsGroup[];
  searchable: boolean | 'auto';
  /** Controlled active id (dialog mode passes the store value). */
  activeId: string | null;
  /** Called when active section changes (dialog mode writes the store). */
  onActiveChange: (id: string) => void;
  /** Section to fall back to when the controlled id is null/invalid. */
  initialSection?: string;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({
  children,
  title,
  sections,
  groups,
  searchable,
  activeId,
  onActiveChange,
  initialSection,
}) => {
  const [query, setQuery] = useState('');

  // Filtered/ordered structure. Search filters the rail but never the lookup map.
  const { groups: resolvedGroups, visible, byId, ids } = useSettingsSections({
    sections,
    groups,
    query,
  });

  // Resolve the active section. Precedence: controlled id (if known) →
  // initialSection (if known) → first visible section → null.
  const fallbackId = useMemo(() => {
    if (initialSection && ids.has(initialSection)) return initialSection;
    return visible[0]?.id ?? sections.find((s) => !s.hidden)?.id ?? null;
  }, [initialSection, ids, visible, sections]);

  const resolvedActiveId =
    activeId && ids.has(activeId) ? activeId : fallbackId;

  const active = resolvedActiveId ? byId.get(resolvedActiveId) ?? null : null;

  const setActive = useCallback(
    (id: string) => {
      // Picking a section clears any search so the panel is reachable.
      setQuery('');
      onActiveChange(id);
    },
    [onActiveChange],
  );

  const value = useMemo<SettingsContextValue>(
    () => ({
      title,
      groups: resolvedGroups,
      visible,
      active,
      activeId: resolvedActiveId,
      setActive,
      query,
      setQuery,
      searchable: searchable === 'auto' ? visible.length >= SEARCH_MIN_SECTIONS : searchable,
    }),
    [title, resolvedGroups, visible, active, resolvedActiveId, setActive, query, searchable],
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
};
