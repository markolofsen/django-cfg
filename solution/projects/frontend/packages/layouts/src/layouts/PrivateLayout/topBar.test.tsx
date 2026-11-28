// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { PrivateLayout } from './PrivateLayout';

vi.mock('next/navigation', () => ({ usePathname: () => '/', useRouter: () => ({ push: () => {}, replace: () => {} }), useSearchParams: () => new URLSearchParams() }));

// PrivateLayout lazy-loads the settings dialog without its own Suspense; keep the test to the shell.
vi.mock('../SettingsLayout/SettingsDialog', () => ({ SettingsDialog: () => null }));
let currentUser: { email: string; display_username: string; avatar: null } | null = { email: 'a@b.c', display_username: 'Mark', avatar: null };
vi.mock('@djangocfg/api/auth', async () => ({
  AuthContext: (await import('react')).createContext(undefined),
  useAuth: () => ({ user: currentUser }),
}));
vi.mock('./hooks/useAuthGuard', () => ({ useAuthGuard: () => ({ isLoading: false, isForbidden: false, loadingText: '' }) }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let phone = true;
let host: HTMLElement | null = null;
let root: Root | null = null;

beforeAll(() => {
  window.matchMedia = ((query: string) => ({
    // A phone has no precise hover pointer; a desktop does.
    matches: query.includes('hover: hover') ? !phone : phone,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false,
  })) as typeof window.matchMedia;
});

afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
  phone = true;
  currentUser = { email: 'a@b.c', display_username: 'Mark', avatar: null };
  document.cookie = 'sidebar_state=; path=/; max-age=0';
});

async function mount(props: Partial<React.ComponentProps<typeof PrivateLayout>>) {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  await act(async () =>
    root!.render(
      <PrivateLayout
        requireAuth={false}
        sidebar={{ groups: [{ label: 'A', items: [{ label: 'Home', href: '/' }] }] }}
        header={{ title: 'Acme' }}
        {...props}
      >
        <p>page</p>
      </PrivateLayout>,
    ),
  );
  return document.querySelector('[data-sidebar="topbar"]');
}

describe('PrivateLayout topBar', () => {
  it('title falls back to header.title', async () => {
    expect((await mount({ topBar: { account: false } }))?.textContent).toBe('Acme');
  });

  it('topBar.title overrides it and topBar.actions render on the right', async () => {
    const bar = (await mount({ topBar: { title: 'Calls', actions: <button>New</button> } }))!;
    expect(bar.textContent).toBe('CallsNewM');
    expect(bar.querySelector('[data-sidebar="topbar-actions"]')!.firstElementChild?.textContent).toBe('New');
  });

  it('desktop, sidebar pinned open: no bar, the account stays in the sidebar footer', async () => {
    phone = false;
    document.cookie = 'sidebar_state=true; path=/';
    await mount({ topBar: { title: 'Calls', actions: <button>New</button> } });
    expect(document.querySelector('[data-sidebar="topbar"]')).toBeNull();
    expect(document.querySelector('[data-sidebar="topbar-account"]')).toBeNull();
    expect(document.body.textContent).toContain('Mark');
  });

  it('desktop, sidebar collapsed: the same bar with title, actions and avatar', async () => {
    phone = false;
    document.cookie = 'sidebar_state=false; path=/';
    const bar = (await mount({ topBar: { title: 'Calls', actions: <button>New</button> } }))!;
    expect(bar.children[1].textContent).toBe('Calls');
    expect(bar.querySelector('[data-sidebar="topbar-actions"]')!.children[1].getAttribute('data-sidebar')).toBe('topbar-account');
  });

  describe('account', () => {
    it('avatar present when signed in', async () => {
      const bar = (await mount({}))!;
      expect(bar.querySelector('[data-sidebar="topbar-account"]')).not.toBeNull();
    });

    it('no avatar without a session', async () => {
      currentUser = null;
      const bar = (await mount({}))!;
      expect(bar.querySelector('[data-sidebar="topbar-account"]')).toBeNull();
    });

    it('no avatar with topBar.account === false', async () => {
      const bar = (await mount({ topBar: { account: false } }))!;
      expect(bar.querySelector('[data-sidebar="topbar-account"]')).toBeNull();
    });

    it('bar avatar and sidebar footer open the same menu items', async () => {
      const labels = async (el: Element) => {
        await act(async () => {
          el.dispatchEvent(new MouseEvent('pointerdown', { bubbles: true, button: 0 }));
          el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, button: 0 }));
          (el as HTMLElement).click();
        });
        const items = [...document.querySelectorAll('[role="menuitem"]')].map((i) => i.textContent);
        await act(async () => {
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
        });
        return items;
      };
      const bar = (await mount({}))!;
      const fromBar = await labels(bar.querySelector('[data-sidebar="topbar-account"]')!);
      expect(fromBar.length).toBeGreaterThan(0);
      await act(async () => root?.unmount());
      host?.remove();
      phone = false;
      document.cookie = 'sidebar_state=true; path=/';
      await mount({});
      const footer = [...document.querySelectorAll('button')].find((b) => b.textContent?.includes('Mark'))!;
      expect(await labels(footer)).toEqual(fromBar);
    });

    async function openDrawer() {
      await act(async () => {
        (document.querySelector('[data-sidebar="trigger"]') as HTMLElement).click();
      });
      return document.querySelector('[data-sidebar="sidebar"][data-mobile="true"]') ?? document.body;
    }

    it('phone drawer has no footer account while the bar carries the avatar', async () => {
      await mount({});
      const drawer = await openDrawer();
      expect(drawer.textContent).toContain('Home');
      expect(document.body.textContent).not.toContain('Mark');
    });

    it('phone drawer shows the footer account again with topBar.account === false', async () => {
      await mount({ topBar: { account: false } });
      await openDrawer();
      expect(document.body.textContent).toContain('Mark');
    });
  });

  describe('toggle', () => {
    it('no tooltip and no native title on desktop or phone; aria-label stays', async () => {
      for (const isPhone of [false, true]) {
        phone = isPhone;
        document.cookie = 'sidebar_state=false; path=/';
        const bar = (await mount({}))!;
        const trigger = bar.querySelector<HTMLElement>('[data-sidebar="trigger"]')!;
        expect(trigger.hasAttribute('data-state')).toBe(false);
        expect(trigger.hasAttribute('title')).toBe(false);
        expect(trigger.getAttribute('aria-label')).toBe('Open sidebar');
        await act(async () => {
          trigger.focus();
          trigger.dispatchEvent(new FocusEvent('focus'));
        });
        expect(document.querySelector('[role="tooltip"]')).toBeNull();
        await act(async () => root?.unmount());
        host?.remove();
        host = root = null;
      }
    });
  });

  describe('hover-open', () => {
    const enter = (el: Element) =>
      act(async () => {
        const ev = new Event('pointerenter', { bubbles: false }) as Event & { pointerType?: string };
        ev.pointerType = 'mouse';
        el.dispatchEvent(ev);
        // React's onPointerEnter listens to pointerover.
        const over = new Event('pointerover', { bubbles: true }) as Event & { pointerType?: string };
        over.pointerType = 'mouse';
        el.dispatchEvent(over);
      });

    it('the bar toggle does not open the hover overlay; the left edge zone does', async () => {
      vi.useFakeTimers();
      try {
        phone = false;
        document.cookie = 'sidebar_state=false; path=/';
        const bar = (await mount({}))!;
        const trigger = bar.querySelector('[data-sidebar="trigger"]')!;
        await enter(trigger);
        await act(async () => { vi.advanceTimersByTime(1000); });
        expect(document.querySelector('[data-sidebar="peek"]')).toBeNull();

        const edge = document.querySelector('[data-sidebar="peek-edge"]')!;
        expect(edge).not.toBeNull();
        await enter(edge);
        await act(async () => { vi.advanceTimersByTime(1000); });
        expect(document.querySelector('[data-sidebar="peek"]')).not.toBeNull();
      } finally {
        vi.useRealTimers();
      }
    });
  });
});
