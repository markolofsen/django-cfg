'use client';

import React, { memo } from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Link } from '@djangocfg/ui-core/components';

import { AUTH } from '../../constants';

export interface AuthHeaderProps {
  logo?: React.ReactNode;
  title: string;
  subtitle?: string;
  identifier?: string;
  /**
   * The brand is already rendered elsewhere on this screen (the `fullsplit`
   * media half). The logo stays in the markup and CSS hides it at the width
   * where that other half is actually visible — see `.auth-header` in
   * `auth.css`. Rendering it conditionally in JS instead would need a width
   * the server does not have, and the brand would flicker on hydration.
   */
  brandElsewhere?: boolean;
  className?: string;
}

/**
 * AuthHeader - Apple-style header with logo, title, and subtitle.
 *
 * `logo` is any React node (inline-SVG brand component, `<img>`, …), rendered
 * inside an `.auth-logo` wrapper so the existing logo sizing/spacing applies.
 * The slot fits the artwork rather than the reverse: a square mark and a
 * horizontal lock-up both keep their aspect ratio.
 */
function AuthHeaderRaw({
  logo,
  title,
  subtitle,
  identifier,
  brandElsewhere = false,
  className = '',
}: AuthHeaderProps) {
  const t = useAppT();
  /*
   * A link, not decoration — so no `aria-hidden`: it is the one way off this
   * screen and must be reachable by keyboard and named for a screen reader.
   * The name comes from the shared catalogue because `logo` is an opaque node
   * this component cannot read a name out of; a brand that is a bare SVG
   * would otherwise announce as an unnamed link.
   */
  const mark = logo ? (
    <Link
      href={AUTH.HOME_URL}
      className="auth-logo"
      aria-label={t('layouts.navigation.home')}
    >
      {logo}
    </Link>
  ) : null;

  return (
    <div className={`auth-header ${className}`} data-brand-elsewhere={brandElsewhere}>
      {mark}
      <h1 className="auth-title">{title}</h1>
      {subtitle && (
        <p className="auth-subtitle" aria-live="polite">
          {subtitle}
          {identifier && (
            <>
              {' '}
              <span className="auth-identifier">{identifier}</span>
            </>
          )}
        </p>
      )}
    </div>
  );
}

export const AuthHeader = memo(AuthHeaderRaw);
