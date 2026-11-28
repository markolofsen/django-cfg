'use client';

import React, { createContext, memo, useContext } from 'react';

import type { AuthShellContextValue } from './types';

const AuthShellContext = createContext<AuthShellContextValue | undefined>(undefined);

interface AuthShellProviderProps {
  value: AuthShellContextValue;
  children: React.ReactNode;
}

/**
 * AuthShellProvider — context wrapper for shell metadata.
 *
 * Memoised: re-renders only when `value` reference or `children` change.
 * The parent (AuthShell) already memoises `value`, so this stabilises
 * the context subtree against unrelated parent renders.
 */
function AuthShellProviderRaw({ value, children }: AuthShellProviderProps) {
  return <AuthShellContext.Provider value={value}>{children}</AuthShellContext.Provider>;
}

export const AuthShellProvider = memo(AuthShellProviderRaw);

export const useAuthShell = (): AuthShellContextValue => {
  const ctx = useContext(AuthShellContext);
  if (!ctx) {
    throw new Error('useAuthShell must be used within an AuthShellProvider');
  }
  return ctx;
};

export const useAuthShellOptional = (): AuthShellContextValue | undefined =>
  useContext(AuthShellContext);
