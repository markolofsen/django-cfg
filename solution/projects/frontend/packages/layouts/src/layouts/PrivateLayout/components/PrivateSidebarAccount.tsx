/**
 * Sidebar account: rich footer trigger (avatar + name + plan + optional secondary
 * action) opens a popover (DropdownMenu) upward with email, account links, and
 * sign-out. Language and theme controls live inside ProfileLayout / PreferencesSection
 * so they are not duplicated here.
 *
 * Reads `isAccountMenuOpen` / `setIsAccountMenuOpen` directly from
 * PrivateLayoutContext so the parent sidebar can block collapse while the menu
 * is open.
 */

'use client';

import { Link } from '@djangocfg/ui-core/components';
import React, { memo } from 'react';

import { useSidebar } from '@djangocfg/ui-core/components';
import { cn, isDev } from '@djangocfg/ui-core/lib';
import { useAuth } from '@djangocfg/api/auth';

import { LucideIcon as LucideIconRender } from '../../../components';
import { AccountFooterTrigger, AccountMenu } from '../../../components/account';
import { usePeekPin } from '../hooks';
import { usePrivateLayoutContext } from '../context';
import { SIDEBAR_SPACING } from '../geometry';

import type { HeaderConfig } from '../types';

interface PrivateSidebarAccountProps {
  header?: HeaderConfig;
}

function PrivateSidebarAccountRaw({ header }: PrivateSidebarAccountProps) {
  const { setOpen: setSidebarOpen } = useSidebar();
  const { isMobile } = usePrivateLayoutContext();
  const [isAccountMenuOpen, setIsAccountMenuOpen] = React.useState(false);
  usePeekPin(isAccountMenuOpen);

  const { user } = useAuth();

  const onSecondaryExpand = React.useCallback(() => {
    setSidebarOpen(true);
  }, [setSidebarOpen]);

  // Hide entirely in production when there's no user (auth still loading or
  // /me failed and the parent guard hasn't redirected yet). In dev keep a
  // placeholder so the footer + Log out are reachable for debugging.
  //
  // EVERY hook must run above this line. When a terminal 401 clears the session,
  // `user` flips to null and this branch starts returning early — if any hook
  // lived below it, the hook count would drop between renders and React would
  // throw #310 ("rendered more hooks than during the previous render"). That is
  // exactly what happened on my.cmdop.com/private/: two hooks sat below and the
  // dashboard white-screened on the 401 transition. It only reproduced in
  // production because `isDev` makes this guard statically dead in development.
  if (!user && !isDev) return null;

  const secondary = header?.footerSecondaryAction;

  const secondaryButton = secondary ? (
    <SecondaryAction action={secondary} onParentExpand={onSecondaryExpand} />
  ) : null;

  const wrapperClass = cn(
    'flex w-full min-w-0 shrink-0 items-center justify-between gap-1 border-t border-sidebar-border/60 bg-sidebar',
    SIDEBAR_SPACING[isMobile ? 'mobile' : 'desktop'].footer,
  );

  return (
    <div className={wrapperClass}>
      {/* Always opens UPWARD over the avatar (Claude pattern): the footer sits at the bottom of the rail. */}
      <AccountMenu
        groups={header?.groups}
        plan={header?.userPlan}
        signIn="none"
        devFallback
        side="top"
        align="start"
        sideOffset={8}
        open={isAccountMenuOpen}
        onOpenChange={setIsAccountMenuOpen}
      >
        <AccountFooterTrigger hasSecondary={Boolean(secondary)} className={isMobile ? 'h-10 px-2.5' : undefined} avatarClassName={isMobile ? 'size-7' : undefined} />
      </AccountMenu>
      {secondaryButton}
    </div>
  );
}

/**
 * Memoised account footer. Re-renders only when the `header` prop reference
 * changes. Internal reactive data (user from useAuth, locale) are
 * consumed via hooks and still update independently.
 */
export const PrivateSidebarAccount = memo(PrivateSidebarAccountRaw);

interface SecondaryActionProps {
  action: NonNullable<HeaderConfig['footerSecondaryAction']>;
  onParentExpand: () => void;
}

function SecondaryAction({ action, onParentExpand }: SecondaryActionProps) {
  // Radix's DropdownMenuTrigger opens on pointerdown, before React onClick fires.
  // Stop the event there too — onClick alone is too late.
  const stop = (e: React.SyntheticEvent) => {
    e.stopPropagation();
    e.preventDefault();
  };

  const handleClick = (e: React.MouseEvent) => {
    stop(e);
    onParentExpand();
    action.onClick?.();
  };

  const inner = (
    <span
      className={cn(
        'relative inline-flex size-7 shrink-0 items-center justify-center rounded-md',
        'bg-transparent text-sidebar-foreground/60',
        'transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground',
      )}
    >
      <LucideIconRender icon={action.icon} className="h-4 w-4" />
      {action.pulse ? (
        <span className="pointer-events-none absolute -right-0.5 -top-0.5 flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
        </span>
      ) : null}
    </span>
  );

  if (action.href) {
    return (
      <Link
        href={action.href}
        aria-label={action.ariaLabel}
        onClick={handleClick}
        onPointerDown={stop}
        onPointerUp={stop}
        data-no-expand
      >
        {inner}
      </Link>
    );
  }

  return (
    <button
      type="button"
      aria-label={action.ariaLabel}
      onClick={handleClick}
      onPointerDown={stop}
      onPointerUp={stop}
      data-no-expand
    >
      {inner}
    </button>
  );
}
