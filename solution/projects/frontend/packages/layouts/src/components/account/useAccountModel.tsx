/**
 * What the account menu shows, shared by every place it can live (sidebar footer, top bar avatar): the user, the
 * display fields and the menu items. One source, so the menus can never drift apart.
 */

'use client';

import React from 'react';

import { useAuth } from '@djangocfg/api/auth';
import type { MenuItem } from '@djangocfg/ui-core/components';

import type { UserMenuGroup, UserMenuLocaleConfig } from '../../layouts/types';
import { useAccountMenuItems } from './useAccountMenuItems';

export interface AccountView {
  source: 'user' | 'dev-fallback';
  displayName: string;
  email: string | null;
  avatarUrl: string;
  plan: string | null;
}

export interface UseAccountModelOptions {
  /** App link groups. */
  groups?: UserMenuGroup[];
  /** Plan shown after the name in the footer trigger. */
  plan?: string | null;
  i18n?: UserMenuLocaleConfig;
  /** Extra items between the groups and Sign out (language, app links). */
  extra?: MenuItem[];
  /** Settings rows in the menu. @default true */
  settings?: boolean;
  /** Identity block above the items: the `email` (default) or a name + email `card`. */
  identity?: 'email' | 'card';
}

export function useAccountModel({ groups, plan = null, i18n, settings = true, extra, identity = 'email' }: UseAccountModelOptions = {}) {
  const { user } = useAuth();

  /**
   * When `useAuth` returns a real user we use it; otherwise (dev only) a placeholder keeps the menu reachable for
   * debugging. Production stays strict: callers render nothing without a user.
   */
  const account = React.useMemo<AccountView>(() => {
    if (user) {
      return {
        source: 'user',
        displayName: user.display_username || user.email || 'User',
        email: user.email ?? null,
        avatarUrl: user.avatar ?? '',
        plan,
      };
    }
    return {
      source: 'dev-fallback',
      displayName: 'Guest (dev)',
      email: null,
      avatarUrl: '',
      plan: plan ?? 'No session',
    };
  }, [user, plan]);

  const headerLabel: React.ReactNode =
    identity === 'card' ? (
      <div className="flex flex-col space-y-1">
        <p className="text-sm font-medium leading-none">{account.displayName}</p>
        <p className="text-xs leading-none text-muted-foreground">{account.email}</p>
      </div>
    ) : (
      account.email ?? (account.source === 'dev-fallback' ? 'No active session' : null)
    );
  const menuItems = useAccountMenuItems({ groups, label: headerLabel, i18n, settings, extra });

  return { user, account, menuItems };
}
