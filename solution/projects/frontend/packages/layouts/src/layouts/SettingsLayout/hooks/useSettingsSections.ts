'use client';

/**
 * useSettingsSections — resolve raw section/group config into the ordered,
 * grouped, search-filtered structure the nav rail renders.
 *
 * Pure derivation (no side effects): built-ins + app sections are merged,
 * hidden ones dropped from the rail, sorted by (group order, section order,
 * declaration index), then partitioned into groups. A search query filters by
 * label text + keywords.
 */

import { useMemo } from 'react';

import type { SettingsGroup, SettingsSection } from '../types';

/** A group paired with its resolved, ordered sections. */
export interface ResolvedGroup {
  id: string;
  label?: React.ReactNode;
  sections: SettingsSection[];
}

export interface UseSettingsSectionsArgs {
  /** Built-in + app sections, already concatenated by the caller. */
  sections: SettingsSection[];
  /** Group definitions for ordering/labelling. */
  groups?: SettingsGroup[];
  /** Live search query (case-insensitive). Empty = no filtering. */
  query?: string;
}

export interface UseSettingsSectionsResult {
  /** Groups (with sections) for the nav rail, in render order. */
  groups: ResolvedGroup[];
  /** Flat list of all visible sections, in render order. */
  visible: SettingsSection[];
  /** Lookup by id across ALL sections (incl. hidden) — for resolving active. */
  byId: Map<string, SettingsSection>;
  /** All known section ids (incl. hidden) — handed to the URL resolver. */
  ids: Set<string>;
}

const DEFAULT_GROUP_ID = '__default__';

/** Extract searchable text from a label that may be a string or JSX. */
function labelText(label: React.ReactNode): string {
  return typeof label === 'string' ? label : '';
}

function matchesQuery(section: SettingsSection, q: string): boolean {
  if (!q) return true;
  const haystack = [
    labelText(section.label),
    labelText(section.title),
    ...(section.keywords ?? []),
  ]
    .join(' ')
    .toLowerCase();
  return haystack.includes(q);
}

export function useSettingsSections({
  sections,
  groups,
  query = '',
}: UseSettingsSectionsArgs): UseSettingsSectionsResult {
  return useMemo(() => {
    const q = query.trim().toLowerCase();

    const byId = new Map<string, SettingsSection>();
    const ids = new Set<string>();
    for (const s of sections) {
      byId.set(s.id, s);
      ids.add(s.id);
    }

    // Group order: explicit `order`, else declaration order; default group first.
    const groupOrder = new Map<string, number>();
    groupOrder.set(DEFAULT_GROUP_ID, -Infinity);
    (groups ?? []).forEach((g, i) => {
      groupOrder.set(g.id, g.order ?? i);
    });
    const groupLabel = new Map<string, React.ReactNode>();
    (groups ?? []).forEach((g) => g.label && groupLabel.set(g.id, g.label));

    // Bucket visible (not hidden, passes search) sections by group.
    const buckets = new Map<string, Array<{ section: SettingsSection; index: number }>>();
    const visible: SettingsSection[] = [];

    sections.forEach((section, index) => {
      if (section.hidden) return;
      if (!matchesQuery(section, q)) return;
      const gid = section.group && groupOrder.has(section.group) ? section.group
        : section.group ?? DEFAULT_GROUP_ID;
      // Register ad-hoc groups (named on a section but not declared) so they sort stably.
      if (!groupOrder.has(gid)) groupOrder.set(gid, buckets.size);
      if (!buckets.has(gid)) buckets.set(gid, []);
      buckets.get(gid)!.push({ section, index });
    });

    // Sort sections within each bucket, then emit groups in group order.
    const resolved: ResolvedGroup[] = [...buckets.entries()]
      .sort((a, b) => (groupOrder.get(a[0])! - groupOrder.get(b[0])!))
      .map(([gid, entries]) => {
        const ordered = entries
          .sort((a, b) => {
            const oa = a.section.order ?? a.index;
            const ob = b.section.order ?? b.index;
            return oa - ob;
          })
          .map((e) => e.section);
        ordered.forEach((s) => visible.push(s));
        return {
          id: gid,
          label: gid === DEFAULT_GROUP_ID ? undefined : groupLabel.get(gid),
          sections: ordered,
        };
      });

    return { groups: resolved, visible, byId, ids };
  }, [sections, groups, query]);
}
