/**
 * Pure helpers over sidebar config: which rows are launchers, what is visible, a stable key.
 * No React and no store, so the rules are tested without rendering.
 */

import type { SidebarGroupConfig, SidebarItem, SidebarLinkItem, SidebarSettingsItem } from './types';

export function isSettingsItem<Id extends string>(item: SidebarItem<Id>): item is SidebarSettingsItem<Id> {
  return typeof item.settingsSection === 'string';
}

export function isLinkItem(item: SidebarItem): item is SidebarLinkItem {
  return typeof item.href === 'string';
}

/** Identity of a row for React keys and memo checks. */
export function sidebarItemKey(item: SidebarItem): string {
  return isSettingsItem(item) ? `settings:${item.settingsSection}` : (item as SidebarLinkItem).href;
}

/**
 * The rows of a group that may render: links always, launchers only for a registered section (no dead door).
 * `registered` is the id set the mounted SettingsDialog lists.
 */
export function visibleSidebarItems(items: SidebarItem[], registered: ReadonlySet<string>): SidebarItem[] {
  return items.filter((item) => !isSettingsItem(item) || registered.has(item.settingsSection));
}

/**
 * Whether a group renders at all. A `dynamic` group needs a row; any group that was given rows needs one of them to
 * survive, so a "Connect" group whose only row is an unregistered section leaves no label and no divider behind.
 * A group declared with no rows keeps its old behaviour (it renders, as a label).
 */
export function isSidebarGroupVisible(group: SidebarGroupConfig, registered: ReadonlySet<string>): boolean {
  if (group.dynamic && group.items.length === 0) return false;
  if (group.items.length === 0) return true;
  return visibleSidebarItems(group.items, registered).length > 0;
}
