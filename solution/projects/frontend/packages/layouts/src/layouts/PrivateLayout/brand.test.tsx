// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { AuthContext } from '@djangocfg/api/auth';
import { LinkProvider, type LinkComponentProps } from '@djangocfg/ui-core/components';

import { ProjectNameProvider } from '../../shared/ProjectContext';
import { PrivateLayout } from './PrivateLayout';

vi.mock('next/navigation', () => ({ usePathname: () => '/', useRouter: () => ({ push: () => {}, replace: () => {} }), useSearchParams: () => new URLSearchParams() }));
vi.mock('../SettingsLayout/SettingsDialog', () => ({ SettingsDialog: () => null }));
vi.mock('@djangocfg/api/auth', async () => ({
  AuthContext: (await import('react')).createContext(undefined),
  useAuth: () => ({ user: null }),
}));
vi.mock('./hooks/useAuthGuard', () => ({ useAuthGuard: () => ({ isLoading: false, isForbidden: false, loadingText: '' }) }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let phone = true;
let host: HTMLElement | null = null;
let root: Root | null = null;
const navigated: string[] = [];

/** A router-style Link: records the navigation instead of loading a page. */
function RouterLink({ href, children, onClick, ...rest }: LinkComponentProps) {
  return (
    <a
      href={href}
      {...(rest as object)}
      onClick={(e) => {
        onClick?.(e);
        e.preventDefault();
        navigated.push(href);
      }}
    >
      {children}
    </a>
  );
}

beforeAll(() => {
  window.matchMedia = ((query: string) => ({
    matches: query.includes('hover: hover') ? !phone : phone,
    media: query, onchange: null,
    addEventListener: () => {}, removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
  })) as typeof window.matchMedia;
});

afterEach(() => {
  act(() => root?.unmount());
  host?.remove();
  host = root = null;
  phone = true;
  navigated.length = 0;
  document.cookie = 'sidebar_state=; path=/; max-age=0';
});

async function mount(props: Partial<React.ComponentProps<typeof PrivateLayout>>, project?: string, landing?: string) {
  host = document.createElement('div');
  document.body.appendChild(host);
  root = createRoot(host);
  await act(async () =>
    root!.render(
      <AuthContext.Provider value={(landing ? { routes: { auth: '/auth', defaultCallback: landing, defaultAuthCallback: '/auth' } } : undefined) as never}>
      <LinkProvider value={RouterLink}>
        <ProjectNameProvider value={project}>
          <PrivateLayout requireAuth={false} sidebar={{ groups: [{ label: 'A', items: [{ label: 'Docs', href: '/docs' }] }] }} {...props}>
            <p>page</p>
          </PrivateLayout>
        </ProjectNameProvider>
      </LinkProvider>
      </AuthContext.Provider>,
    ),
  );
}

const bar = () => document.querySelector('[data-sidebar="topbar"]');
const barLink = () => bar()?.querySelector('a') ?? null;

async function openDrawer() {
  await act(async () => {
    (document.querySelector('[data-sidebar="trigger"]') as HTMLElement).click();
  });
}
const drawerBrand = () =>
  document.querySelector('[data-sidebar="header"] a') as HTMLAnchorElement | null;

describe('brand link and title resolution', () => {
  it('bar title links to "/" by default', async () => {
    await mount({ header: { title: 'Acme' } });
    expect(barLink()?.getAttribute('href')).toBe('/');
    expect(barLink()?.textContent).toBe('Acme');
    expect(barLink()?.getAttribute('aria-label')).toBe('Acme');
  });

  it('header.href sets the target; click goes through the router link', async () => {
    await mount({ header: { title: 'Acme', href: '/app' } });
    expect(barLink()?.getAttribute('href')).toBe('/app');
    await act(async () => barLink()!.click());
    expect(navigated).toEqual(['/app']);
  });

  it('topBar.title stays as given, not linkified', async () => {
    await mount({ header: { title: 'Acme' }, topBar: { title: 'Calls' } });
    expect(bar()?.textContent).toContain('Calls');
    expect(barLink()).toBeNull();
  });

  it('drawer brand links home and closes the drawer on click', async () => {
    await mount({ header: { title: 'Acme', href: '/app' } });
    await openDrawer();
    const link = drawerBrand()!;
    expect(link.getAttribute('href')).toBe('/app');
    expect(link.textContent).toContain('Acme');
    expect(document.querySelector('[data-sidebar="sidebar"][data-mobile="true"], [role="dialog"]')).not.toBeNull();
    await act(async () => link.click());
    expect(navigated).toEqual(['/app']);
    expect(document.querySelector('[role="dialog"][data-state="open"]')).toBeNull();
  });

  it('a custom brand node is rendered as given, not wrapped in a link', async () => {
    await mount({ header: { title: 'Acme', brand: <b data-testid="mine">Mine</b> } }, undefined);
    phone = false;
    await act(async () => root?.unmount());
    host?.remove();
    document.cookie = 'sidebar_state=true; path=/';
    await mount({ header: { title: 'Acme', brand: <b data-testid="mine">Mine</b> } });
    const mine = document.querySelector('[data-testid="mine"]')!;
    expect(mine.closest('a')).toBeNull();
  });

  it('no header.title: the project name from the provider is shown and linked', async () => {
    await mount({}, 'Proj');
    expect(barLink()?.textContent).toBe('Proj');
    expect(barLink()?.getAttribute('href')).toBe('/');
  });

  it('explicit header.title wins over the project name', async () => {
    await mount({ header: { title: 'Acme' } }, 'Proj');
    expect(barLink()?.textContent).toBe('Acme');
  });

  it('no provider and no title: no text, no crash, no empty bar link', async () => {
    await mount({});
    expect(bar()).not.toBeNull();
    expect(barLink()).toBeNull();
    await openDrawer();
    const link = drawerBrand();
    expect(link?.getAttribute('aria-label')).toBe('Home');
    expect(link?.textContent?.trim().length).toBeLessThanOrEqual(1);
  });

  describe('home href resolution: header.href > sidebar.homeHref > auth defaultCallback > "/"', () => {
    it('auth provider defaultCallback is the target when nothing else is set', async () => {
      await mount({ header: { title: 'Acme' } }, undefined, '/workspace');
      expect(barLink()?.getAttribute('href')).toBe('/workspace');
      await openDrawer();
      expect(drawerBrand()?.getAttribute('href')).toBe('/workspace');
    });

    it('sidebar.homeHref beats defaultCallback; header.href beats both', async () => {
      await mount({ header: { title: 'Acme' }, sidebar: { homeHref: '/home', groups: [] } }, undefined, '/workspace');
      expect(barLink()?.getAttribute('href')).toBe('/home');
      await act(async () => root?.unmount());
      host?.remove();
      await mount({ header: { title: 'Acme', href: '/x' }, sidebar: { homeHref: '/home', groups: [] } }, undefined, '/workspace');
      expect(barLink()?.getAttribute('href')).toBe('/x');
    });

    it('outside the auth provider: "/", no crash', async () => {
      await mount({ header: { title: 'Acme' } });
      expect(barLink()?.getAttribute('href')).toBe('/');
    });
  });

  describe('sidebar header toggle', () => {
    it('phone drawer header is the brand only: no toggle button, the link stays, accessible name present', async () => {
      await mount({ header: { title: 'Acme' } });
      await openDrawer();
      const header = document.querySelector('[data-sidebar="header"]')!;
      expect(header.querySelector('button')).toBeNull();
      expect(header.querySelector('[data-sidebar="trigger"]')).toBeNull();
      expect(header.querySelector('a')?.textContent).toContain('Acme');
      // The primitive keeps an sr-only title for screen readers.
      expect(document.querySelector('[role="dialog"] .sr-only')?.textContent).toContain('Sidebar');
    });

    it('phone drawer closes on Escape', async () => {
      await mount({ header: { title: 'Acme' } });
      await openDrawer();
      expect(document.querySelector('[role="dialog"][data-state="open"]')).not.toBeNull();
      await act(async () => {
        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
      });
      expect(document.querySelector('[role="dialog"][data-state="open"]')).toBeNull();
    });

    it('desktop docked sidebar header keeps its toggle', async () => {
      phone = false;
      document.cookie = 'sidebar_state=true; path=/';
      await mount({ header: { title: 'Acme' } });
      expect(document.querySelector('[data-sidebar="header"] [data-sidebar="trigger"]')).not.toBeNull();
    });
  });
});
