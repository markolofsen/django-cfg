'use client';

import React, { memo, useMemo } from 'react';

import { useAppT } from '@djangocfg/i18n';

export interface AuthDividerProps {
  text?: string;
  className?: string;
}

/**
 * AuthDivider - Minimal "or" divider.
 *
 * Memoised: re-renders only when `text` or `className` change.
 * The default translation is memoised internally so it does not
 * break the comparison on every render.
 */
function AuthDividerRaw({
  text,
  className = '',
}: AuthDividerProps) {
  const t = useAppT();
  const defaultText = useMemo(() => t('layouts.auth.divider.or'), [t]);
  const dividerText = text ?? defaultText;

  return (
    <div className={`auth-divider ${className}`}>
      {dividerText}
    </div>
  );
}

export const AuthDivider = memo(AuthDividerRaw);
