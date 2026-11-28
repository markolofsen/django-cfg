'use client';

import React from 'react';

import type { MenuItem } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { AccountAvatarTrigger, AccountFooterTrigger, AccountMenu } from '../../../components/account';

export interface AccountMenuButtonProps {
  /** `row`: avatar, name and chevron (a sidebar footer; the menu opens up). `avatar`: the avatar alone (a header; the menu opens down). */
  variant?: 'row' | 'avatar';
  /** Items between the Settings shortcuts and Sign out (language, app links). */
  extra?: MenuItem[];
  /** Small muted text after the name (a plan). */
  plan?: string | null;
  className?: string;
  /**
   * Class hooks for the parts of the `row` trigger, so a host can restyle them without forking: a collapsed rail
   * hides `name` and `chevron` from its own container query and centres the avatar.
   */
  classNames?: { avatar?: string; name?: string; chevron?: string };
}

/**
 * The ready user menu: the shared `AccountMenu` with a row or avatar trigger. Drop it into any chrome; renders
 * nothing for a signed-out visitor.
 */
export const AccountMenuButton: React.FC<AccountMenuButtonProps> = ({ variant = 'row', extra, plan, className, classNames }) => {
  const isRow = variant === 'row';
  return (
    <AccountMenu
      plan={plan}
      extra={extra}
      signIn="none"
      side={isRow ? 'top' : 'bottom'}
      align={isRow ? 'start' : 'end'}
    >
      {isRow ? (
        <AccountFooterTrigger
          className={cn('h-9', className)}
          avatarClassName={classNames?.avatar}
          nameClassName={classNames?.name}
          chevronClassName={classNames?.chevron}
        />
      ) : (
        <AccountAvatarTrigger className={className} />
      )}
    </AccountMenu>
  );
};
