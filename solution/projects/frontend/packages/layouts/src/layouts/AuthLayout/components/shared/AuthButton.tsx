'use client';

import React, { memo } from 'react';

export interface AuthButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  loading?: boolean;
  children: React.ReactNode;
}

/**
 * AuthButton - Apple-style button with loading state.
 *
 * Memoised: re-renders only when variant, loading, disabled, className or
 * children change. Event handlers passed via ...props are compared by
 * reference — the caller should stabilise them with useCallback.
 */
function AuthButtonRaw({
  variant = 'primary',
  loading = false,
  disabled,
  children,
  className = '',
  ...props
}: AuthButtonProps) {
  const variantClass = `auth-button-${variant}`;
  const loadingClass = loading ? 'auth-button-loading' : '';

  return (
    <button
      type="submit"
      className={`auth-button ${variantClass} ${loadingClass} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {children}
    </button>
  );
}

export const AuthButton = memo(AuthButtonRaw);
