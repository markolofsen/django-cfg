'use client';

import React, { memo } from 'react';

import { ChevronLeft } from 'lucide-react';

import { useAppT } from '@djangocfg/i18n';
import { Link } from '@djangocfg/ui-core/components';

import { LocaleSwitcher } from '../../../_components/LocaleSwitcher';
import { useLayoutI18nOptional } from '../../../../shared/LayoutI18nProvider';
import { AUTH } from '../../constants';

export interface AuthTopBarProps {
  /**
   * The brand already sits on the media half, which links home itself, so the
   * bar stands its own link down where that half is visible (>= 1024px). CSS
   * owns the breakpoint — see `.auth-topbar` in `auth.css`.
   */
  brandPanel?: boolean;
  className?: string;
}

/**
 * AuthTopBar — the one place a sign-in screen keeps its way out and its language.
 *
 * Home on the left, locale on the right, pinned to the top of the viewport and
 * independent of what the app passes. Both used to ride inside the centered
 * form stack: the locale floated above the title, and the way out existed only
 * as the `logo` — an optional prop, hidden with the media half on a phone. An
 * app that passed a custom `sidebar` and no `logo` (the Kino sign-in) left a
 * phone visitor with no route off the screen at all.
 *
 * The link is a real `<a>` to `AUTH.HOME_URL` with a visible label, the way an
 * iOS back button names its destination: an arrow alone reads as browser Back,
 * and Back has nowhere to go when the page was opened by a direct link.
 */
function AuthTopBarRaw({ brandPanel = false, className = '' }: AuthTopBarProps) {
  const t = useAppT();
  const i18n = useLayoutI18nOptional();

  return (
    <div className={`auth-topbar ${className}`} data-brand-panel={brandPanel}>
      <Link href={AUTH.HOME_URL} className="auth-topbar__home">
        <ChevronLeft aria-hidden="true" className="auth-topbar__icon" />
        <span>{t('layouts.navigation.home')}</span>
      </Link>
      {/* Mounted whenever LayoutI18nProvider is — BaseApp does it when the host
          passes `i18n` — so there is no prop to gate it on. */}
      {i18n ? (
        <LocaleSwitcher
          variant="dropdown"
          buttonVariant="ghost"
          size="sm"
          showFlag
          showCode={false}
          showTriggerLabel
          className="auth-locale-trigger"
        />
      ) : null}
    </div>
  );
}

export const AuthTopBar = memo(AuthTopBarRaw);
