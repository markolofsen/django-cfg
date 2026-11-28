'use client';

import React, { memo, useMemo } from 'react';

import { useAppT } from '@djangocfg/i18n';

export interface AuthFooterProps {
  termsUrl?: string;
  privacyUrl?: string;
  supportUrl?: string;
  className?: string;
}

/**
 * AuthFooter - Minimal link row for terms, privacy, and support.
 *
 * Memoised: re-renders only when URL props or className change.
 * Translation labels are derived inside the component via useMemo
 * so they do not break memoisation.
 */
function AuthFooterRaw({
  termsUrl,
  privacyUrl,
  supportUrl,
  className = '',
}: AuthFooterProps) {
  const t = useAppT();
  const labels = useMemo(() => ({
    terms: t('layouts.auth.footer.terms'),
    privacy: t('layouts.auth.footer.privacy'),
    support: t('layouts.auth.footer.support'),
  }), [t]);

  const links = [
    termsUrl && { href: termsUrl, label: labels.terms },
    privacyUrl && { href: privacyUrl, label: labels.privacy },
    supportUrl && { href: supportUrl, label: labels.support },
  ].filter(Boolean) as { href: string; label: string }[];

  if (links.length === 0) {
    return null;
  }

  return (
    <div className={`auth-footer ${className}`}>
      {links.map((link, index) => (
        <React.Fragment key={link.href}>
          {index > 0 && <span className="auth-footer-dot">&middot;</span>}
          <a
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
          >
            {link.label}
          </a>
        </React.Fragment>
      ))}
    </div>
  );
}

export const AuthFooter = memo(AuthFooterRaw);
