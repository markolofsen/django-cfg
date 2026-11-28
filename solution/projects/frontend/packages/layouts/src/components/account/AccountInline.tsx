/**
 * The account menu as an inline list (the phone drawer of PublicLayout, where a dropdown inside a drawer is awkward):
 * identity card, app link groups, Language buttons, Sign out. Same model and labels as `AccountMenu`; only the view differs.
 */

'use client';

import { LogOut } from 'lucide-react';
import { Link } from '@djangocfg/ui-core/components';
import React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { LanguageFlag } from '@djangocfg/ui-core/components';

import { useLogout } from '../../hooks';
import { LOCALE_LABELS } from '../../layouts/_components/LocaleSwitcher';
import type { UserMenuGroup, UserMenuLocaleConfig } from '../../layouts/types';
import { AccountSignInRow } from './AccountMenu';
import { UserAvatar } from './UserAvatar';
import { useAccountModel } from './useAccountModel';

export interface AccountInlineProps {
  groups?: UserMenuGroup[];
  authPath?: string;
  i18n?: UserMenuLocaleConfig;
}

export function AccountInline({ groups, authPath, i18n }: AccountInlineProps) {
  const { user, account } = useAccountModel({ groups, i18n, settings: false });
  const handleLogout = useLogout();
  const t = useAppT();
  const languageLabel = t('layouts.profile.language');
  const signOutLabel = t('layouts.profile.signOut');

  if (!user) return <AccountSignInRow authPath={authPath} />;

  const localeCodes = i18n?.locales?.length ? i18n : null;
  const localeLabel = (code: string) => LOCALE_LABELS[code] || code.toUpperCase();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-popover)] bg-accent/30">
        <UserAvatar src={account.avatarUrl} name={account.displayName} size="md" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground truncate">{account.displayName}</p>
          <p className="text-xs text-muted-foreground truncate">{account.email}</p>
        </div>
      </div>
      <div className="space-y-1">
        {(groups ?? []).map((group, groupIndex) => (
          <div key={groupIndex}>
            {group.title && (
              <div className="px-4 pt-2 pb-1">
                <p className="text-[11px] font-normal text-muted-foreground/70">{group.title}</p>
              </div>
            )}
            {group.items.map((item, itemIndex) => {
              const Icon = item.icon;
              const baseClasses = `flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-sm transition-colors w-full text-left ${
                item.variant === 'destructive'
                  ? 'text-destructive hover:bg-destructive/10'
                  : 'text-foreground hover:bg-accent hover:text-accent-foreground'
              }`;
              if (item.onClick) {
                return (
                  <button key={itemIndex} onClick={item.onClick} className={baseClasses}>
                    {Icon && <Icon className="h-4 w-4" />}
                    {item.label}
                  </button>
                );
              }
              if (item.href) {
                return (
                  <Link key={itemIndex} href={item.href} className={baseClasses}>
                    {Icon && <Icon className="h-4 w-4" />}
                    {item.label}
                  </Link>
                );
              }
              return null;
            })}
          </div>
        ))}
        {localeCodes && (
          <div className="border-t border-border/50 px-4 pt-3">
            <p className="text-[11px] font-normal text-muted-foreground/70">{languageLabel}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {localeCodes.locales.map((code) => {
                const active = code === localeCodes.locale;
                return (
                  <button
                    key={code}
                    type="button"
                    onClick={() => localeCodes.onLocaleChange(code)}
                    className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-sm font-medium transition-colors ${
                      active
                        ? 'border-primary bg-accent text-foreground'
                        : 'border-border/60 text-muted-foreground hover:bg-accent hover:text-foreground'
                    }`}
                  >
                    <LanguageFlag code={code} className="h-3 w-4" rounded />
                    {localeLabel(code)}
                  </button>
                );
              })}
            </div>
          </div>
        )}
        <div>
          <button
            type="button"
            onClick={() => handleLogout()}
            className="flex w-full items-center gap-3 rounded-sm px-4 py-3 text-left text-sm font-medium text-destructive transition-colors hover:bg-destructive/10"
          >
            <LogOut className="h-4 w-4" />
            {signOutLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
