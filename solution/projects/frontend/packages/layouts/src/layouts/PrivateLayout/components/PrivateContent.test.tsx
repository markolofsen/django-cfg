// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { SidebarProvider } from '@djangocfg/ui-core/components';

import { PrivateContent } from './PrivateContent';

vi.mock('@djangocfg/api/auth', () => ({ useAuth: () => ({ user: { email: 'a@b.c', display_username: 'Mark', avatar: null } }) }));
vi.mock('next/navigation', () => ({ usePathname: () => '/', useRouter: () => ({ push: () => {}, replace: () => {} }), useSearchParams: () => new URLSearchParams() }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let phone = false;
let host: HTMLElement | null = null;
let root: Root | null = null;

beforeAll(() => {
  window.matchMedia ??= ((query: string) => ({
    matches: phone,
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
  phone = false;
});

function render(defaultOpen: boolean, padding: 'none' | 'default', title?: React.ReactNode, actions?: React.ReactNode, showAccount = false) {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  act(() =>
    root!.render(
      <SidebarProvider defaultOpen={defaultOpen}>
        <PrivateContent title={title} actions={actions} showAccount={showAccount} padding={padding} scroll={padding === 'none' ? 'hidden' : 'auto'}>
          <p>page</p>
          <input aria-label="field" />
        </PrivateContent>
      </SidebarProvider>,
    ),
  );
  return host;
}

describe('PrivateContent top bar', () => {
  it.each(['none', 'default'] as const)('desktop, sidebar collapsed: the same overlay bar, content offset by its real height (padding %s)', (padding) => {
    const el = render(false, padding);
    const bar = el.querySelector('[data-sidebar="topbar"]')!;
    const col = bar.parentElement as HTMLElement;
    expect(bar).not.toBeNull();
    expect(col.style.getPropertyValue('--layout-bar-height')).toContain('3rem');
    expect(bar.className).toContain('h-[var(--layout-bar-height)]');
    expect(bar.className).toContain('pt-[var(--safe-top');
    expect(bar.className).toMatch(/\babsolute\b/);
    expect(bar.querySelector('[data-sidebar="trigger"]')).not.toBeNull();
    expect((bar.nextElementSibling as HTMLElement).className).toContain('layout-bar-height');
  });

  it('draws no bar while the sidebar is docked, and the bar height is 0', () => {
    const el = render(true, 'default');
    expect(el.querySelector('[data-sidebar="topbar"]')).toBeNull();
    expect(el.querySelector<HTMLElement>('[style*="--layout-bar-height"]')!.style.getPropertyValue('--layout-bar-height')).toBe('0px');
  });

  it.each(['none', 'default'] as const)('phone + padding %s: one fixed-height in-flow bar, the same for every page', (padding) => {
    phone = true;
    const el = render(false, padding, 'Acme');
    const bar = el.querySelector('[data-sidebar="topbar"]')!;
    const col = bar.parentElement as HTMLElement;
    expect(col.style.getPropertyValue('--layout-bar-height')).toBe('calc(var(--safe-top, env(safe-area-inset-top, 0px)) + 3rem)');
    expect(bar.className).toContain('h-[var(--layout-bar-height)]');
    expect(bar.className).toMatch(/\bborder-b\b/);
    expect(bar.className).toContain('bg-background');
    expect(bar.className).toContain('pt-[var(--safe-top');
    expect(bar.className).toContain('pl-[calc(var(--safe-left');
    expect(bar.className).toContain('pr-[calc(var(--safe-right');
    // Overlays the column; the content pads by the bar height. It never moves on scroll.
    expect(bar.className).toMatch(/\babsolute\b/);
    expect(bar.className).not.toContain('translate');
    expect(bar.hasAttribute('data-hidden')).toBe(false);
    expect((bar.nextElementSibling as HTMLElement).className).toContain('layout-bar-height');
    expect(bar.querySelector('[data-sidebar="trigger"]')!.className).not.toMatch(/\b(rounded-full|border|shadow)/);
    expect(bar.textContent).toBe('Acme');
    // Content is the next sibling: it starts under the bar and carries no trigger offsets.
    const scroller = bar.nextElementSibling as HTMLElement;
    expect(scroller.className).not.toContain('layout-trigger');
  });

  it('phone without a title shows the toggle only; desktop sets the bar height to 0', () => {
    phone = true;
    expect(render(false, 'default').querySelector('[data-sidebar="topbar"]')!.textContent).toBe('');
  });

  it('top bar is shrink-0 and the content below it is flex-1 min-h-0 (document cannot grow)', () => {
    const el = render(false, 'default');
    const bar = el.querySelector('[data-sidebar="topbar"]')!;
    const col = bar.parentElement!;
    const scroller = bar.nextElementSibling as HTMLElement;
    expect(bar.className).toMatch(/\bshrink-0\b/);
    expect(col.className).toMatch(/\bmin-h-0\b/);
    expect(scroller.className).toMatch(/\bmin-h-0\b/);
    expect(scroller.className).toMatch(/\bflex-1\b/);
    expect(scroller.className).toMatch(/\boverflow-y-auto\b/);
  });

  it('never hides on scroll, on a phone or on desktop', () => {
    for (const isPhone of [true, false]) {
      phone = isPhone;
      const bar = render(false, 'default', 'Acme').querySelector('[data-sidebar="topbar"]') as HTMLElement;
      const scroller = bar.nextElementSibling as HTMLElement;
      scroller.scrollTop = 400;
      scroller.dispatchEvent(new Event('scroll'));
      expect(bar.hasAttribute('data-hidden')).toBe(false);
      expect(bar.className).not.toContain('translate');
    }
  });

  describe('topBar content', () => {
    it('renders title and right-hand actions; the toggle stays first and does not shrink', () => {
      phone = true;
      const bar = render(false, 'default', 'Calls', <button>New</button>).querySelector('[data-sidebar="topbar"]')!;
      const children = [...bar.children];
      expect(children[0].getAttribute('data-sidebar')).toBe('trigger');
      expect(children[0].className).toMatch(/\bshrink-0\b/);
      const title = children[1] as HTMLElement;
      expect(title.textContent).toBe('Calls');
      expect(title.className).toContain('truncate');
      expect(title.className).toContain('flex-1');
      const actions = children[2] as HTMLElement;
      expect(actions.className).toMatch(/\bshrink-0\b/);
      expect(actions.className).toContain('items-center');
      expect(actions.textContent).toBe('New');
    });

    it('desktop, sidebar collapsed: same markup, title and actions', () => {
      const bar = render(false, 'default', 'Calls', <button>New</button>).querySelector('[data-sidebar="topbar"]')!;
      expect(bar.children[0].getAttribute('data-sidebar')).toBe('trigger');
      expect(bar.children[1].textContent).toBe('Calls');
      expect(bar.children[2].textContent).toBe('New');
    });

    it('account avatar: after the actions, in the actions container, only with showAccount', () => {
      phone = true;
      const bar = render(false, 'default', 'Calls', <button>New</button>, true).querySelector('[data-sidebar="topbar"]')!;
      const actions = bar.querySelector('[data-sidebar="topbar-actions"]')!;
      expect(actions.children[0].textContent).toBe('New');
      expect(actions.children[1].getAttribute('data-sidebar')).toBe('topbar-account');
      expect(actions.children[1].getAttribute('aria-label')).toBe('User menu');
    });

    it('no avatar without showAccount', () => {
      phone = true;
      const bar = render(false, 'default', 'Calls').querySelector('[data-sidebar="topbar"]')!;
      expect(bar.querySelector('[data-sidebar="topbar-account"]')).toBeNull();
      expect(bar.querySelector('[data-sidebar="topbar-actions"]')).toBeNull();
    });
  });
});
