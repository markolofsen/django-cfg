'use client';

import { createContext, useContext } from 'react';

import type { AccountView } from './useAccountModel';

export const AccountViewContext = createContext<{ account: AccountView } | null>(null);

/** The account the surrounding `AccountMenu` shows (triggers read it instead of asking auth again). */
export function useAccountView(): AccountView {
  const ctx = useContext(AccountViewContext);
  if (!ctx) throw new Error('Account triggers must be rendered inside <AccountMenu>.');
  return ctx.account;
}
