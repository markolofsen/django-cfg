/**
 * Triggers for `AccountMenu`. Both are plain forwardRef buttons so the menu can attach to them.
 *  - `AccountAvatarTrigger`: the avatar alone, for bars and navbars (36px hit area, 32px avatar).
 *  - `AccountFooterTrigger`: avatar, name, plan and chevron, for the sidebar footer.
 */

'use client';

import { ChevronDown } from 'lucide-react';
import React from 'react';

import { Avatar, AvatarFallback, AvatarImage, Button } from '@djangocfg/ui-core/components';
import { useAppT } from '@djangocfg/i18n';
import { cn } from '@djangocfg/ui-core/lib';

import { useAccountView } from './accountContext';
import { UserAvatar } from './UserAvatar';

type ButtonProps = React.ComponentProps<typeof Button>;

export interface AccountAvatarTriggerProps extends ButtonProps {
  /** Ring around the avatar (the public navbar look). */
  ring?: boolean;
}

export const AccountAvatarTrigger = React.forwardRef<HTMLButtonElement, AccountAvatarTriggerProps>(
  ({ ring = false, className, ...props }, ref) => {
    const account = useAccountView();
    const t = useAppT();
    return (
      <Button
        ref={ref}
        type="button"
        variant="ghost"
        size="icon"
        data-sidebar="topbar-account"
        aria-label={t('layouts.profile.userMenu') || 'Account'}
        className={cn(ring ? 'rounded-full p-0' : undefined, className)}
        {...props}
      >
        <UserAvatar
          src={account.avatarUrl}
          name={account.displayName}
          size="sm"
          className={ring ? undefined : 'ring-0 hover:ring-0'}
        />
      </Button>
    );
  },
);
AccountAvatarTrigger.displayName = 'AccountAvatarTrigger';

export interface AccountFooterTriggerProps extends ButtonProps {
  avatarClassName?: string;
  nameClassName?: string;
  chevronClassName?: string;
  /** Another control shares the footer row, so this trigger does not take the full width. */
  hasSecondary?: boolean;
}

export const AccountFooterTrigger = React.forwardRef<HTMLButtonElement, AccountFooterTriggerProps>(
  ({ avatarClassName, nameClassName, chevronClassName, hasSecondary = false, className, ...props }, ref) => {
    const account = useAccountView();
    const initial = (account.displayName.charAt(0) || '?').toUpperCase();
    return (
      <Button
        ref={ref}
        type="button"
        variant="ghost"
        className={cn(
          'group h-8 min-w-0 max-w-full justify-start gap-2 rounded-lg px-2 text-left font-normal select-none',
          !hasSecondary && 'w-full',
          'hover:bg-sidebar-accent/70 hover:text-sidebar-foreground',
          // No focus ring on the menu trigger: the open menu is the affordance.
          'focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0',
          className,
        )}
        {...props}
      >
        <Avatar className={cn('size-6 shrink-0', avatarClassName)}>
          <AvatarImage src={account.avatarUrl} alt={account.displayName} />
          <AvatarFallback className="text-xs font-medium">{initial}</AvatarFallback>
        </Avatar>
        <span className={cn('flex min-w-0 items-baseline gap-1 text-left', nameClassName)}>
          <span className="truncate text-sm text-sidebar-foreground">{account.displayName}</span>
          {account.plan ? <span className="shrink-0 text-xs text-sidebar-foreground/50">· {account.plan}</span> : null}
        </span>
        <ChevronDown
          className={cn(
            'size-4 shrink-0 text-sidebar-foreground/40 transition-transform duration-150 group-data-[state=open]:rotate-180',
            !hasSecondary && 'ml-auto',
            chevronClassName,
          )}
          aria-hidden
        />
      </Button>
    );
  },
);
AccountFooterTrigger.displayName = 'AccountFooterTrigger';
