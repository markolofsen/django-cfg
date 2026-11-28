'use client';

import React, { memo } from 'react';

export interface AuthErrorProps {
  message?: string | null;
  className?: string;
}

/**
 * AuthError - Subtle error display with shake animation.
 *
 * Memoised: re-renders only when `message` or `className` change.
 * Returns null when message is empty — the null branch is stable.
 */
function AuthErrorRaw({
  message,
  className = '',
}: AuthErrorProps) {
  if (!message) {
    return null;
  }

  return (
    <div className={`auth-error ${className}`} role="alert" aria-live="assertive">
      <svg
        className="auth-error-icon"
        viewBox="0 0 16 16"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 3.5a.75.75 0 0 1 .75.75v3a.75.75 0 0 1-1.5 0v-3A.75.75 0 0 1 8 4.5zm0 6.5a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5z" />
      </svg>
      <span>{message}</span>
    </div>
  );
}

export const AuthError = memo(AuthErrorRaw);
