/**
 * Private Layout
 *
 * Authenticated shell: a docked, resizable sidebar + scrollable content.
 * Collapsed, the sidebar leaves a trigger whose hover zone peeks it open over the page;
 * on narrow viewports the same trigger opens a drawer. Ctrl/Cmd + B toggles it.
 *
 * Guarded: no session redirects to `header.authPath`. With `requireStaff`, a
 * signed-in non-staff user gets `ForbiddenState` instead — never a redirect,
 * since signing in again cannot grant the privilege.
 */

'use client';

import React from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useLandingRoute } from './hooks/useLandingRoute';
import { useProjectName } from '../../shared/ProjectContext';
import { Preloader } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { SHELL_CLASS } from './geometry';
import { SidebarInset, SidebarProvider } from '@djangocfg/ui-core/components';

import { ForbiddenState, PrivateContent, PrivateSidebar } from './components';
import {
  SidebarPeekProvider,
  SidebarWidthContext,
  useAuthGuard,
  useLayoutVisual,
  useSidebarDefaultOpen,
  useSidebarWidth,
} from './hooks';

import type { PrivateLayoutProps } from './types';

export type {
  SidebarItem,
  SidebarLinkItem,
  SidebarSettingsItem,
  SidebarGroupConfig,
  SidebarConfig,
  HeaderConfig,
  SidebarActiveIndicator,
  SidebarGroupLabelStyle,
  SidebarFeaturedConfig,
  SidebarBrandSwitcherConfig,
  SidebarBrandSwitcherItem,
} from './types';

export { SidebarBrandSwitcher } from './components';

export { PrivateLayoutProps };

const SettingsDialog = React.lazy(() =>
  import('../SettingsLayout/SettingsDialog').then((m) => ({ default: m.SettingsDialog }))
);

export function PrivateLayout({
  children,
  sidebar,
  header,
  topBar,
  pathname,
  contentPadding = 'default',
  contentScroll = 'auto',
  visual,
  requireAuth = true,
  requireStaff = false,
  forbiddenFallback,
  settings,
}: PrivateLayoutProps) {
  const { isLoading, isForbidden, loadingText } = useAuthGuard({
    requireAuth,
    requireStaff,
    authPath: header?.authPath,
  });

  const { providerStyle, providerClassName, insetClassName, sidebarVariant } =
    useLayoutVisual(visual);

  // The account avatar lives in the top bar for a signed-in user unless `topBar.account === false`.
  const { user } = useAuth();
  // Bar title: topBar.title > header.title > the BaseApp project name > nothing. Only the last two link home.
  const projectName = useProjectName();
  const landing = useLandingRoute();
  const barTitle = topBar?.title ?? (header?.title?.trim() || projectName || undefined);
  const barHref = header?.href || sidebar?.homeHref || landing || '/';
  const accountInBar = Boolean(user) && topBar?.account !== false;

  const defaultOpen = useSidebarDefaultOpen();
  const sidebarWidth = useSidebarWidth(Boolean(sidebar) && sidebar?.resizable !== false);

  // Marks <html> while a private shell is mounted: base.css locks html/body (no document scroll, no rubber band)
  // in an installed app, for private pages only. Public pages never carry it and stay scrollable.
  React.useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-private-shell', '');
    return () => root.removeAttribute('data-private-shell');
  }, []);

  if (isLoading) {
    return (
      // The auth gate covers the whole viewport: solid, above the chat dock (z-100), sheets, dialogs and popovers.
      // Nothing behind it may show or take a click while the session is still being decided.
      <Preloader
        variant="fullscreen"
        text={loadingText}
        size="lg"
        backdrop={false}
        className="z-[9996] bg-background"
      />
    );
  }

  // Before the shell: a forbidden user must never reach the sidebar or the
  // children, or every request they trigger returns 403 and the screen cannot
  // be told apart from a backend outage.
  if (isForbidden) {
    return <>{forbiddenFallback ?? <ForbiddenState />}</>;
  }

  return (
    <SidebarProvider
      defaultOpen={defaultOpen}
      style={{ ...providerStyle, ...sidebarWidth.style }}
      className={cn(SHELL_CLASS, providerClassName)}
      // Named for `syncViewport` (ui-core): the clipped shell is put back at scroll 0.
      data-app-shell=""
      data-sidebar-resizing={sidebarWidth.dragging || undefined}
    >
      <SidebarWidthContext.Provider value={sidebarWidth}>
        <SidebarPeekProvider pathname={pathname ?? ''}>
          {sidebar && (
            <PrivateSidebar
              sidebar={sidebar}
              header={header}
              pathname={pathname}
              variant={sidebarVariant}
              accountInBar={accountInBar}
            />
          )}

          <SidebarInset className={insetClassName}>
            <PrivateContent
              padding={contentPadding}
              scroll={contentScroll}
              hasSidebar={Boolean(sidebar)}
              pathname={pathname}
              title={barTitle}
              titleHref={topBar?.title == null && barTitle ? barHref : undefined}
              actions={topBar?.actions}
              showAccount={accountInBar}
              header={header}
              visual={visual}
            >
              {children}
            </PrivateContent>
          </SidebarInset>
        </SidebarPeekProvider>
      </SidebarWidthContext.Provider>

      {/* Settings is the primary account dialog — always mounted so the
          account-menu "Settings" item works out of the box. `settings` is
          optional config (extra app sections / flags), not an on/off switch. */}
      <SettingsDialog {...(settings ?? {})} />
    </SidebarProvider>
  );
}
