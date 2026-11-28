/**
 * User menu for the public navbar and its phone drawer. A thin wrapper over the shared account menu
 * (`components/account`): `desktop` is the avatar dropdown, `mobile` the inline list. Props are unchanged.
 *
 * @example
 * <UserMenu groups={[{ title: 'Account', items: [{ label: 'Profile', href: '/profile' }] }]} authPath="/auth" />
 */

'use client';

import React from 'react';

import { AccountAvatarTrigger, AccountInline, AccountMenu } from '../../../components/account';
import type { UserMenuGroup, UserMenuLocaleConfig } from '../../types';

export interface UserMenuProps {
  /** Display variant */
  variant?: 'desktop' | 'mobile';
  /** Menu groups for authenticated users */
  groups?: UserMenuGroup[];
  /** Auth page path (for sign in button) */
  authPath?: string;
  /** Disable the sign-in button (guest state, auth not available) */
  disableAuth?: boolean;
  /**
   * Language switching inside this menu (desktop: submenu; mobile: button row).
   * Prefer this over nesting `<LocaleSwitcher />` in the same dropdown: nested menus close each other.
   */
  i18n?: UserMenuLocaleConfig;
}

export function UserMenu({ variant = 'desktop', groups, authPath, disableAuth = false, i18n }: UserMenuProps) {
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  if (variant === 'mobile') {
    return <AccountInline groups={groups} authPath={authPath} i18n={i18n} />;
  }

  return (
    <AccountMenu
      groups={groups}
      i18n={i18n}
      authPath={authPath}
      settings={false}
      identity="card"
      signIn={disableAuth ? 'disabled' : 'button'}
      side="bottom"
      align="end"
      sideOffset={4}
      contentClassName="w-56"
    >
      <AccountAvatarTrigger ring />
    </AccountMenu>
  );
}
