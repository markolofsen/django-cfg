import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { useEffect } from 'react';
import { Home } from 'lucide-react';

import { LayoutI18nProvider, PrivateLayout, type HeaderConfig, type SidebarConfig } from '@djangocfg/layouts';
import { MockAuthProvider, buildMockUser } from '@djangocfg/layouts/testing';
import { Button, Drawer, DrawerContent, DrawerTitle, DrawerTrigger } from '@djangocfg/ui-core/components';
import { getViewportLog, syncViewport, syncViewportDebug, viewportSnapshot } from '@djangocfg/ui-core/hooks';
import { ThemeProvider } from '@djangocfg/ui-core/theme';

/**
 * A locked `PrivateLayout` you can displace on purpose, to exercise `syncViewport` (ui-core `hooks/media/viewportSync`)
 * and the Debug section of Settings (`settings={{ builtins: { debug: true } }}`) without an iPhone. It is only locked in an installed app: open it with `?sb-device=pwa`
 * (see the Device toolbar). Buttons push the shell and the window off 0, or open a drawer;
 * the shell must be back at 0 within a few frames. Playwright reads `window.__shellDisplacement.state()`.
 *
 * WebKit (Playwright `webkit`) is the closest engine to iOS Safari available on a desktop. It is NOT iOS standalone:
 * it has no real keyboard, no `visualViewport` inset and no home-screen display mode (emulated here), so this proves the
 * scroll-back logic, not that the phone behaves.
 */

const SIDEBAR: SidebarConfig = {
  homeHref: '/home',
  groups: [{ label: '', items: [{ label: 'Home', href: '/home', icon: Home }] }],
};
const HEADER: HeaderConfig = { title: 'Calls' };

const shellEl = () => document.querySelector<HTMLElement>('[data-app-shell]');

const api = {
  /** Scrolls the clipped shell, the way focus does. */
  displaceShell: (px = 59) => { const el = shellEl(); if (el) el.scrollTop = px; },
  /** Scrolls the window (needs the document taller than the screen: the story adds 100px of it). */
  displaceWindow: (px = 59) => window.scrollTo(0, px),
  state: () => ({ shellTop: shellEl()?.scrollTop ?? null, scrollY: window.scrollY, bodyStyle: document.body.style.cssText, resets: getViewportLog().map((r) => r.trigger) }),
  snapshot: viewportSnapshot,
};

function Harness() {
  useEffect(() => {
    (window as unknown as { __shellDisplacement: typeof api }).__shellDisplacement = api;
    const stopReset = syncViewport();
    const stopHud = syncViewportDebug();
    document.documentElement.style.minHeight = 'calc(100% + 100px)';
    return () => { stopReset(); stopHud(); document.documentElement.style.minHeight = ''; };
  }, []);
  return (
    <div className="flex flex-col gap-3 p-4">
      <p className="text-sm text-muted-foreground">Use the Device toolbar: PWA phone. Each button should snap back to 0.</p>
      <div className="flex flex-wrap gap-2">
        <Button data-testid="displace-shell" onClick={() => api.displaceShell()}>Displace shell</Button>
        <Button data-testid="displace-window" onClick={() => api.displaceWindow()}>Displace window</Button>
        <Drawer>
          <DrawerTrigger asChild><Button data-testid="open-drawer" variant="secondary">Open drawer</Button></DrawerTrigger>
          <DrawerContent><DrawerTitle className="p-4">Close me, then look at the top bar</DrawerTitle></DrawerContent>
        </Drawer>
      </div>
    </div>
  );
}

function ShellDisplacement() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="shell-displacement-theme">
      <MockAuthProvider user={buildMockUser()}>
        <LayoutI18nProvider value={{ locale: 'en', locales: ['en'], onLocaleChange: () => undefined }}>
          <PrivateLayout sidebar={SIDEBAR} header={HEADER} pathname="/calls" requireAuth={false} settings={{ syncUrl: false, sections: [], builtins: { debug: true } }}>
            <Harness />
          </PrivateLayout>
        </LayoutI18nProvider>
      </MockAuthProvider>
    </ThemeProvider>
  );
}

const meta = {
  title: 'Layouts/Shell displacement',
  component: ShellDisplacement,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof ShellDisplacement>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Locked: Story = { globals: { displayMode: 'standalone', safeArea: 'iphone' } };
