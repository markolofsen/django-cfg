/**
 * Account avatar for the top bar: the shared `AccountMenu` (the same items as the sidebar footer) opened downward
 * and aligned to the right edge. Rendered only for a signed-in user; the caller decides whether the bar shows it.
 */

'use client';

import React from 'react';

import { AccountAvatarTrigger, AccountMenu } from '../../../components/account';

import type { HeaderConfig } from '../types';

export function PrivateTopBarAccount({ header }: { header?: HeaderConfig }) {
  return (
    <AccountMenu
      groups={header?.groups}
      plan={header?.userPlan}
      signIn="none"
      side="bottom"
      align="end"
      sideOffset={6}
    >
      <AccountAvatarTrigger />
    </AccountMenu>
  );
}
