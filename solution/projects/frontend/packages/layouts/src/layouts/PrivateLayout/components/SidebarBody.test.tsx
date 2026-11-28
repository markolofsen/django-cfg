// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { SidebarProvider } from '@djangocfg/ui-core/components';

import { PrivateLayoutProvider } from '../context';
import { SIDEBAR_SPACING } from '../geometry';
import { SidebarBody } from './SidebarBody';

vi.mock('@djangocfg/api/auth', async () => ({
  AuthContext: (await import('react')).createContext(undefined),
  useAuth: () => ({ user: { email: 'a@b.c', display_username: 'Mark' } }),
}));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLElement | null = null;
let root: Root | null = null;

beforeAll(() => {
  window.matchMedia ??= ((query: string) => ({
    matches: false, media: query, onchange: null,
    addEventListener: () => {}, removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
  })) as typeof window.matchMedia;
});
afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
});

function render(isMobile: boolean) {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  act(() =>
    root!.render(
      <SidebarProvider>
        <PrivateLayoutProvider sidebar={{ groups: [{ label: 'A', items: [{ label: 'Home', href: '/' }] }] }} header={undefined} pathname="/" isMobile={isMobile}>
          <SidebarBody />
        </PrivateLayoutProvider>
      </SidebarProvider>,
    ),
  );
  return host;
}

describe('SidebarBody zones', () => {
  it.each([true, false])('header and footer are pinned (shrink-0), only the nav scrolls (mobile %s)', (isMobile) => {
    const el = render(isMobile);
    const header = el.querySelector<HTMLElement>('[data-sidebar="header"]')!;
    const nav = el.querySelector<HTMLElement>('[data-sidebar="content"]')!;
    const footer = nav.nextElementSibling as HTMLElement;
    expect(header.className).toMatch(/\bshrink-0\b/);
    expect(header.className).toContain('bg-sidebar');
    expect(nav.className).toMatch(/\bmin-h-0\b/);
    expect(nav.className).toMatch(/\bflex-1\b/);
    expect(nav.className).toMatch(/\boverflow-y-auto\b/);
    expect(nav.className).toMatch(/\boverscroll-contain\b/);
    expect(footer.className).toMatch(/\bshrink-0\b/);
    expect(footer.className).toMatch(/\bborder-t\b/);
    expect(footer.className).toContain('bg-sidebar');
    // Nothing else in the body scrolls.
    expect(header.className).not.toMatch(/overflow-y-auto/);
    expect(footer.className).not.toMatch(/overflow-y-auto/);
  });

  it('mobile footer respects the home indicator', () => {
    expect(SIDEBAR_SPACING.mobile.footer).toContain('--safe-bottom');
  });
});
