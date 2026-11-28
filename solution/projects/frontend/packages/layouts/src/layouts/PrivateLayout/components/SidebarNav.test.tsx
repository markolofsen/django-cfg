// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';

import { SidebarProvider } from '@djangocfg/ui-core/components';

import { useSettingsDialogStore } from '../../SettingsLayout/store';
import { PrivateLayoutProvider } from '../context';
import { mcpSidebarGroup } from '../mcpSidebar';
import type { SidebarConfig, SidebarGroupConfig } from '../types';
import { SidebarNavGroup } from './SidebarNavGroup';

// react-dom + jsdom only: the package declares no testing-library.
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLElement | null = null;
let root: Root | null = null;

/** Elements by ARIA role and accessible text (own text content), enough for these rows. */
const screen = {
  all(selector: string, name?: string): HTMLElement[] {
    const found = Array.from(host?.querySelectorAll<HTMLElement>(selector) ?? []);
    return name === undefined ? found : found.filter((el) => el.textContent?.trim() === name);
  },
  link: (name: string) => screen.all('a[href]', name)[0] ?? null,
  button: (name: string) => screen.all('button', name)[0] ?? null,
  separators: () => screen.all('[role="separator"]'),
  text: (value: string) => screen.all('span, div, p', value)[0] ?? null,
};

beforeAll(() => {
  // jsdom has no matchMedia; the sidebar's mobile check reads it.
  window.matchMedia ??= ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false,
  })) as typeof window.matchMedia;
});

const registerSections = (...ids: string[]) =>
  useSettingsDialogStore.setState({ sections: ids.map((id) => ({ id, label: id })) });

function renderGroups(groups: SidebarGroupConfig[], pathname = '/') {
  const sidebar: SidebarConfig = { groups };
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  act(() => root!.render(
    <SidebarProvider>
      <PrivateLayoutProvider sidebar={sidebar} header={undefined} pathname={pathname} isMobile={false}>
        {groups.map((group, i) => (
          <SidebarNavGroup key={i} group={group} />
        ))}
      </PrivateLayoutProvider>
    </SidebarProvider>,
  ));
}

const main: SidebarGroupConfig = { label: 'Main', items: [{ label: 'Home', href: '/' }, { label: 'Reports', href: '/reports' }] };
const connect = mcpSidebarGroup({ label: 'Connect', itemLabel: 'MCP' });

beforeEach(() => {
  useSettingsDialogStore.setState({ sections: [], isOpen: false, activeSection: null, intent: null });
});
afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
});

describe('href rows (unchanged)', () => {
  it('render as links and mark the current route', () => {
    renderGroups([main], '/reports');
    const reports = screen.link('Reports')!;
    expect(reports.getAttribute('href')).toBe('/reports');
    expect(reports.getAttribute('aria-current')).toBe('page');
    expect(screen.link('Home')!.getAttribute('aria-current')).toBeNull();
    expect(screen.separators()).toHaveLength(0);
  });
});

describe('settingsSection rows', () => {
  it('render nothing, and no group, while the section is not registered', () => {
    renderGroups([main, connect]);
    expect(screen.button('MCP')).toBeNull();
    expect(screen.text('Connect')).toBeNull();
    expect(screen.separators()).toHaveLength(0);
  });

  it('appear once the section is registered, and open the dialog on it', () => {
    registerSections('account', 'mcp');
    renderGroups([main, connect]);
    act(() => screen.button('MCP')!.click());
    const state = useSettingsDialogStore.getState();
    expect(state.isOpen).toBe(true);
    expect(state.activeSection).toBe('mcp');
  });

  it('are active only while the dialog shows that section', () => {
    registerSections('account', 'mcp');
    renderGroups([main, connect]);
    const row = () => screen.button('MCP')!;
    expect(row().getAttribute('aria-current')).toBeNull();

    act(() => useSettingsDialogStore.getState().open('account'));
    expect(row().getAttribute('aria-current')).toBeNull();

    act(() => useSettingsDialogStore.getState().open('mcp'));
    expect(row().getAttribute('aria-current')).toBe('true');
    expect(row().getAttribute('data-active')).toBe('true');

    act(() => useSettingsDialogStore.getState().close());
    expect(row().getAttribute('aria-current')).toBeNull();
  });

  it('do not take over the route highlight of href rows', () => {
    registerSections('mcp');
    renderGroups([main, connect], '/');
    expect(screen.link('Home')!.getAttribute('aria-current')).toBe('page');
  });
});

describe('separated groups', () => {
  it('draw a divider above the label', () => {
    registerSections('mcp');
    renderGroups([main, connect]);
    const separators = screen.separators();
    expect(separators).toHaveLength(1);
    const divider = separators[0]!;
    const label = screen.text('Connect')!;
    expect(divider.compareDocumentPosition(label) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(divider.getAttribute('data-sidebar')).toBe('group-divider');
  });

  it('draw a bare divider when the label is empty', () => {
    registerSections('mcp');
    renderGroups([main, mcpSidebarGroup({ label: '' })]);
    expect(screen.separators()).toHaveLength(1);
    expect(screen.button('MCP')).not.toBeNull();
  });

  it('are not drawn for ordinary groups', () => {
    renderGroups([main, { label: 'More', items: [{ label: 'Docs', href: '/docs' }] }]);
    expect(screen.separators()).toHaveLength(0);
  });
});
