// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { AccountAvatarTrigger, AccountFooterTrigger, AccountMenu } from './index';

let currentUser: { email: string; display_username: string; avatar: null } | null = null;
vi.mock('@djangocfg/api/auth', () => ({
  useAuth: () => ({ user: currentUser, routes: { auth: '/auth' }, logout: () => {} }),
}));
vi.mock('next/navigation', () => ({ usePathname: () => '/', useRouter: () => ({ push: () => {}, replace: () => {} }) }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const GROUPS = [{ items: [{ label: 'Billing', href: '/billing' }, { label: 'Team', href: '/team' }] }];

let host: HTMLElement | null = null;
let root: Root | null = null;

beforeAll(() => {
  window.matchMedia = ((query: string) => ({
    matches: false, media: query, onchange: null,
    addEventListener: () => {}, removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
  })) as typeof window.matchMedia;
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver ??= class { observe() {} unobserve() {} disconnect() {} };
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.scrollIntoView ??= () => {};
});

afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
  currentUser = null;
  document.body.innerHTML = '';
});

async function mount(node: React.ReactElement) {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  await act(async () => root!.render(node));
}

async function openMenu() {
  const trigger = host!.querySelector('button')!;
  await act(async () => {
    trigger.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, button: 0, pointerType: 'mouse' }));
    trigger.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
}

const menuText = () => Array.from(document.querySelectorAll('[role="menu"] [role="menuitem"]')).map((e) => e.textContent?.trim());
const menuEl = () => document.querySelector('[role="menu"]') as HTMLElement | null;

describe('AccountMenu', () => {
  it('signed in: groups and Sign out', async () => {
    currentUser = { email: 'a@b.c', display_username: 'Mark', avatar: null };
    await mount(<AccountMenu groups={GROUPS}><AccountAvatarTrigger /></AccountMenu>);
    await openMenu();
    const items = menuText();
    expect(items).toContain('Billing');
    expect(items).toContain('Team');
    expect(items.some((t) => /sign out|log out|logout/i.test(t ?? ''))).toBe(true);
  });

  it('signed out: a sign-in link to the auth route, no menu trigger', async () => {
    await mount(<AccountMenu groups={GROUPS}><AccountAvatarTrigger /></AccountMenu>);
    const a = host!.querySelector('a');
    expect(a?.getAttribute('href')).toBe('/auth');
    expect(host!.querySelector('[aria-haspopup="menu"]')).toBeNull();
  });

  it('signed out with authPath: link goes there; signIn="none" renders nothing', async () => {
    await mount(<AccountMenu authPath="/login"><AccountAvatarTrigger /></AccountMenu>);
    expect(host!.querySelector('a')?.getAttribute('href')).toBe('/login');
    act(() => root!.render(<AccountMenu signIn="none"><AccountAvatarTrigger /></AccountMenu>));
    expect(host!.innerHTML).toBe('');
  });

  it('the avatar and footer triggers open the same items', async () => {
    currentUser = { email: 'a@b.c', display_username: 'Mark', avatar: null };
    await mount(<AccountMenu groups={GROUPS} plan="Pro"><AccountAvatarTrigger /></AccountMenu>);
    await openMenu();
    const fromAvatar = menuText();
    act(() => root?.unmount());
    host?.remove();
    document.body.innerHTML = '';
    await mount(<AccountMenu groups={GROUPS} plan="Pro"><AccountFooterTrigger /></AccountMenu>);
    expect(host!.textContent).toContain('Pro');
    await openMenu();
    expect(menuText()).toEqual(fromAvatar);
  });

  it('side and align are passed to the menu content', async () => {
    currentUser = { email: 'a@b.c', display_username: 'Mark', avatar: null };
    await mount(<AccountMenu side="top" align="start" groups={GROUPS}><AccountFooterTrigger /></AccountMenu>);
    await openMenu();
    const el = menuEl();
    expect(el?.getAttribute('data-side')).toBe('top');
    expect(el?.getAttribute('data-align')).toBe('start');
  });

  it('avatar fallback shows the initial', async () => {
    currentUser = { email: 'zed@b.c', display_username: 'Zed', avatar: null };
    await mount(<AccountMenu><AccountAvatarTrigger /></AccountMenu>);
    expect(host!.textContent).toContain('Z');
  });
});
