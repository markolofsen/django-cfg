'use client';

import React, { memo } from 'react';

export interface AuthLinkProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  href?: string;
}

/**
 * AuthLink - Text link styled button/anchor.
 *
 * Memoised: re-renders only when `href`, `className`, `children` or
 * event handlers change. Callers should stabilise `onClick` with
 * useCallback to avoid unnecessary re-renders.
 */
function AuthLinkRaw({
  children,
  href,
  className = '',
  ...props
}: AuthLinkProps) {
  if (href) {
    return (
      <a
        href={href}
        className={`auth-link ${className}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    );
  }

  return (
    <button
      type="button"
      className={`auth-link ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export const AuthLink = memo(AuthLinkRaw);
