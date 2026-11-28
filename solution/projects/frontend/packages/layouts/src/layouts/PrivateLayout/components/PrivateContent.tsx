/**
 * Private layout main column: the scroll surface, plus ONE top bar whenever the sidebar is not visible: always on a
 * phone (below md), on desktop while the sidebar is collapsed. Same markup and props at every width: sidebar toggle,
 * title, actions, account avatar. Height `--layout-bar-height` = safe-top + 3rem; it overlays the column and the
 * content has that height as top padding, so pages need to know nothing about it. It never hides on scroll (owner decision,
 * 2026-11-05: it got in the way): static at every width.
 * `--layout-bar-height` is `0px` only when no bar is shown (docked sidebar, or no sidebar at all).
 */

'use client';

import React, { ReactNode } from 'react';

import { Link, useSidebar } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import type { LayoutVisualConfig } from '../../types';
import type { HeaderConfig } from '../types';
import { LAYOUT_BAR_HEIGHT } from '../geometry';
import { PrivateSidebarTrigger } from './PrivateSidebarTrigger';
import { PrivateTopBarAccount } from './PrivateTopBarAccount';

interface PrivateContentProps {
  children: ReactNode;
  padding?: 'none' | 'default';
  /**
   * Controls the overflow behaviour of the scroll surface.
   * - `'auto'` (default) — content scrolls vertically inside the shell.
   * - `'hidden'` — shell does NOT scroll; children must manage their own scroll.
   *   Use this for full-height pages like Kanban where columns scroll individually.
   */
  scroll?: 'auto' | 'hidden';
  /** When false, no mobile hamburger (e.g. layout without a sidebar). Default true. */
  hasSidebar?: boolean;
  /** A change scrolls the content surface back to the top (the document no longer scrolls, so the router cannot). */
  pathname?: string;
  /** Bar title next to the toggle (`topBar.title`, else `header.title`). */
  title?: ReactNode;
  /** When set, the title is a router link to this href (the default `header.title` fallback only). */
  titleHref?: string;
  /** Bar right-hand actions (`topBar.actions`), left of the account avatar. */
  actions?: ReactNode;
  /** Show the account avatar at the right end of the bar (signed-in user and `topBar.account !== false`). */
  showAccount?: boolean;
  /** Account menu config (links, plan) for the avatar. */
  header?: HeaderConfig;
  /** Visual config from PrivateLayout — controls maxWidth in boxed mode. */
  visual?: LayoutVisualConfig;
}

const MAX_WIDTH_CLASS: Record<NonNullable<LayoutVisualConfig['maxWidth']>, string> = {
  none: '',
  '7xl': 'mx-auto w-full max-w-7xl',
  'screen-xl': 'mx-auto w-full max-w-screen-xl',
  'screen-2xl': 'mx-auto w-full max-w-screen-2xl',
};

export function PrivateContent({
  children,
  padding = 'default',
  scroll = 'auto',
  hasSidebar = true,
  visual,
  pathname,
  title,
  titleHref,
  actions,
  showAccount = false,
  header,
}: PrivateContentProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const lastPath = React.useRef(pathname);
  React.useEffect(() => {
    if (lastPath.current === pathname) return;
    lastPath.current = pathname;
    scrollRef.current?.scrollTo?.({ top: 0 });
  }, [pathname]);

  const { isMobile, state } = useSidebar();

  const showBar = hasSidebar && (isMobile || state === 'collapsed');

  const topPadding = showBar
    ? 'pt-[calc(var(--layout-bar-height)+1rem)]'
    : hasSidebar
      ? 'pt-6 lg:pt-8'
      : 'pt-4 sm:pt-6 lg:pt-8';

  const scrollAreaClass = cn(
    'min-h-0 flex-1 bg-background',
    // The bar overlays the column, so every page starts below it.
    showBar && padding === 'none' && 'pt-[var(--layout-bar-height)]',
    scroll === 'auto' ? 'overflow-y-auto' : 'flex flex-col overflow-hidden',
    padding === 'default' && scroll === 'auto' && [
      'px-4 sm:px-6 lg:px-8',
      'pb-[calc(1rem+var(--safe-bottom,env(safe-area-inset-bottom,0px)))] sm:pb-[calc(1.5rem+var(--safe-bottom,env(safe-area-inset-bottom,0px)))] lg:pb-[calc(2rem+var(--safe-bottom,env(safe-area-inset-bottom,0px)))]',
      topPadding,
    ],
  );

  const innerWidthClass = MAX_WIDTH_CLASS[visual?.maxWidth ?? 'none'];

  return (
    <div
      className="relative flex min-h-0 min-w-0 flex-1 flex-col"
      style={{ '--layout-bar-height': showBar ? LAYOUT_BAR_HEIGHT : '0px' } as React.CSSProperties}
    >
      {showBar ? (
        <div
          data-sidebar="topbar"
          className="absolute inset-x-0 top-0 z-20 box-border flex h-[var(--layout-bar-height)] shrink-0 items-center gap-1 border-b border-border bg-background pl-[calc(var(--safe-left,env(safe-area-inset-left,0px))+0.75rem)] pr-[calc(var(--safe-right,env(safe-area-inset-right,0px))+0.75rem)] pt-[var(--safe-top,env(safe-area-inset-top,0px))]"
        >
          <PrivateSidebarTrigger className="text-muted-foreground hover:text-foreground" />
          <span className="min-w-0 flex-1 truncate text-base font-semibold tracking-tight">
            {titleHref ? (
              <Link
                href={titleHref}
                aria-label={typeof title === 'string' && title ? title : 'Home'}
                className="rounded-md text-foreground no-underline outline-none ring-ring pointer-coarse:block pointer-coarse:w-fit pointer-coarse:max-w-full pointer-coarse:truncate pointer-coarse:py-2.5 transition-opacity hover:no-underline hover:opacity-80 focus-visible:ring-2"
              >
                {title}
              </Link>
            ) : (
              title
            )}
          </span>
          {actions || showAccount ? (
            <div data-sidebar="topbar-actions" className="flex shrink-0 items-center gap-2">
              {actions}
              {showAccount ? <PrivateTopBarAccount header={header} /> : null}
            </div>
          ) : null}
        </div>
      ) : null}
      <div ref={scrollRef} className={scrollAreaClass}>
        {innerWidthClass ? <div className={innerWidthClass}>{children}</div> : children}
      </div>
    </div>
  );
}
