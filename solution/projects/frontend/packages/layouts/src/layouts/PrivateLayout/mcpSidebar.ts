/**
 * Ready sidebar entries for the MCP section (`mcpSettingsSection()` from `@djangocfg/widget-mcp`).
 *
 * They name the section by id only (`MCP_SECTION_ID`), so layouts holds no import of the widget. They render only
 * while the host registered that section: add them to the config unconditionally.
 */

import type { LucideIcon } from 'lucide-react';

import { MCP_SECTION_ID } from '../SettingsLayout/sectionIds';
import type { SidebarGroupConfig, SidebarSettingsItem } from './types';

export interface McpSidebarItemOptions {
  /** The row's text. The host's to translate. */
  label: string;
  /** Lucide icon name or component. Default `"Cable"`. */
  icon?: string | LucideIcon;
}

export interface McpSidebarGroupOptions extends Partial<McpSidebarItemOptions> {
  /** The group's label, under the divider. Use `''` for a bare divider. */
  label: string;
  /** The row's text. Default `"MCP"` (a product name, not translated). */
  itemLabel?: string;
}

/** A row that opens Settings on the MCP section; hidden while the section is not registered. */
export function mcpSidebarItem({ label, icon = 'Cable' }: McpSidebarItemOptions): SidebarSettingsItem<typeof MCP_SECTION_ID> {
  return { label, icon, settingsSection: MCP_SECTION_ID };
}

/** A separated group holding the MCP row; the whole group is hidden while the section is not registered. */
export function mcpSidebarGroup({ label, itemLabel = 'MCP', icon }: McpSidebarGroupOptions): SidebarGroupConfig<typeof MCP_SECTION_ID> {
  return { label, separated: true, items: [mcpSidebarItem({ label: itemLabel, icon })] };
}
