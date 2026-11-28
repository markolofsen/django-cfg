import { describe, expect, it } from 'vitest';

import { mcpSidebarGroup, mcpSidebarItem } from './mcpSidebar';
import { isSidebarGroupVisible, sidebarItemKey, visibleSidebarItems } from './sidebarItems';
import type { SidebarGroupConfig, SidebarItem } from './types';

const link: SidebarItem = { label: 'Home', href: '/' };
const mcp = mcpSidebarItem({ label: 'MCP' });
const none: ReadonlySet<string> = new Set();
const withMcp: ReadonlySet<string> = new Set(['account', 'mcp']);

describe('visibleSidebarItems', () => {
  it('keeps links whatever is registered', () => {
    expect(visibleSidebarItems([link], none)).toEqual([link]);
  });

  it('drops a launcher for a section that is not registered (no dead door)', () => {
    expect(visibleSidebarItems([link, mcp], none)).toEqual([link]);
    expect(visibleSidebarItems([link, mcp], withMcp)).toEqual([link, mcp]);
  });
});

describe('isSidebarGroupVisible', () => {
  it('hides a group whose launchers are all unregistered, label and divider with it', () => {
    const group = mcpSidebarGroup({ label: 'Connect' });
    expect(isSidebarGroupVisible(group, none)).toBe(false);
    expect(isSidebarGroupVisible(group, withMcp)).toBe(true);
  });

  it('keeps a mixed group while one row survives', () => {
    const group: SidebarGroupConfig = { label: 'Tools', items: [link, mcp] };
    expect(isSidebarGroupVisible(group, none)).toBe(true);
  });

  it('keeps the old rules for href-only groups', () => {
    expect(isSidebarGroupVisible({ label: 'A', items: [link] }, none)).toBe(true);
    expect(isSidebarGroupVisible({ label: 'A', items: [], dynamic: true }, none)).toBe(false);
    expect(isSidebarGroupVisible({ label: 'A', items: [] }, none)).toBe(true);
  });
});

describe('keys and the MCP defaults', () => {
  it('keys a link by href and a launcher by section', () => {
    expect(sidebarItemKey(link)).toBe('/');
    expect(sidebarItemKey(mcp)).toBe('settings:mcp');
  });

  it('mcpSidebarItem defaults the icon to Cable and names the section by id only', () => {
    expect(mcp).toEqual({ label: 'MCP', icon: 'Cable', settingsSection: 'mcp' });
    expect(mcpSidebarItem({ label: 'X', icon: 'Plug' }).icon).toBe('Plug');
  });

  it('mcpSidebarGroup is a separated group with one MCP row', () => {
    const group = mcpSidebarGroup({ label: 'Connect', itemLabel: 'Assistants' });
    expect(group).toMatchObject({ label: 'Connect', separated: true });
    expect(group.items).toEqual([{ label: 'Assistants', icon: 'Cable', settingsSection: 'mcp' }]);
  });
});
