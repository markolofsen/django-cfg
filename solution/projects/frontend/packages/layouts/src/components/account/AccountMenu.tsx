/**
 * The ONE account menu. Content (identity, Settings rows, app link groups, Language, Sign out) comes from
 * `useAccountModel`; placement is the caller's: pass a trigger as `children` (`AccountAvatarTrigger` for bars and
 * navbars, `AccountFooterTrigger` for the sidebar footer) and the side/align the menu should open to.
 *
 *   public navbar (top right)      <AccountMenu side="bottom" align="end" settings={false}><AccountAvatarTrigger ring/></AccountMenu>
 *   private bar (top right)        <AccountMenu side="bottom" align="end"><AccountAvatarTrigger/></AccountMenu>
 *   sidebar footer                 <AccountMenu side="top" align="start"><AccountFooterTrigger/></AccountMenu>
 *
 * A signed-out visitor gets the sign-in button (`signIn="button"`), a disabled one, or nothing.
 */

'use client';

import { ArrowRight } from 'lucide-react';
import React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Button, Link, MenuBuilder } from '@djangocfg/ui-core/components';
import { useAuth } from '@djangocfg/api/auth';
import { isDev } from '@djangocfg/ui-core/lib';

import { AccountViewContext } from './accountContext';
import { useAccountModel, type UseAccountModelOptions } from './useAccountModel';
import { AccountAvatarTrigger } from './triggers';

export interface AccountMenuProps extends UseAccountModelOptions {
  /** Trigger. Default: the avatar button. */
  children?: React.ReactElement;
  side?: 'top' | 'bottom' | 'left' | 'right';
  align?: 'start' | 'center' | 'end';
  sideOffset?: number;
  contentClassName?: string;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Signed-out visitor: a sign-in `button` (default), a `disabled` one, or `none`. */
  signIn?: 'button' | 'disabled' | 'none';
  /** Auth page for the sign-in button; defaults to the auth route. */
  authPath?: string;
  /** Show a placeholder account without a session in development, so the menu stays reachable. */
  devFallback?: boolean;
}

export function AccountMenu({
  children,
  side = 'bottom',
  align = 'end',
  sideOffset = 8,
  contentClassName = 'w-60 p-1.5',
  open,
  onOpenChange,
  signIn = 'button',
  authPath,
  devFallback = false,
  ...model
}: AccountMenuProps) {
  const { user, account, menuItems } = useAccountModel(model);
  const { routes } = useAuth();
  const t = useAppT();
  const [innerOpen, setInnerOpen] = React.useState(false);
  const isOpen = open ?? innerOpen;
  const setOpen = onOpenChange ?? setInnerOpen;

  const view = React.useMemo(() => ({ account }), [account]);

  if (!user && !(devFallback && isDev)) {
    if (signIn === 'none') return null;
    const label = t('layouts.profile.login');
    if (signIn === 'disabled') {
      return (
        <Button variant="default" size="sm" className="h-9 rounded-full px-5" disabled>
          {label}
        </Button>
      );
    }
    return (
      <Link href={authPath ?? routes.auth}>
        <Button variant="default" size="sm" className="h-9 rounded-full px-5">
          {label}
        </Button>
      </Link>
    );
  }

  return (
    <AccountViewContext.Provider value={view}>
      <MenuBuilder
        items={menuItems}
        open={isOpen}
        onOpenChange={setOpen}
        side={side}
        align={align}
        sideOffset={sideOffset}
        contentClassName={contentClassName}
      >
        {children ?? <AccountAvatarTrigger />}
      </MenuBuilder>
    </AccountViewContext.Provider>
  );
}

/** The sign-in row used in the phone drawer (inline variant). */
export function AccountSignInRow({ authPath }: { authPath?: string }) {
  const { routes } = useAuth();
  const t = useAppT();
  return (
    <div className="pt-4 border-t border-border/50">
      <Link
        href={authPath ?? routes.auth}
        className="group flex items-center justify-between rounded-control px-4 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground hover:bg-accent/40"
      >
        <span>{t('layouts.profile.login')}</span>
        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
      </Link>
    </div>
  );
}
