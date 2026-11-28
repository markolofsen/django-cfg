'use client';

import { useCallback } from 'react';

import { type UseOAuthLoginOptions, useOAuthLogin } from './useOAuthLogin';

export type { OAuthUser } from './useOAuthLogin';

/** @deprecated Use `UseOAuthLoginOptions`. */
export type UseGithubAuthOptions = UseOAuthLoginOptions;

/** @deprecated Use `UseOAuthLoginReturn`. */
export interface UseGithubAuthReturn {
  isLoading: boolean;
  error: string | null;
  startGithubAuth: () => Promise<void>;
  handleGithubCallback: (code: string, state: string) => Promise<void>;
}

/**
 * @deprecated Use `useOAuthLogin` (`start('github')`, `complete('github', code, state)`).
 * Kept for one minor release; behaviour is `useOAuthLogin` with the provider fixed.
 */
export const useGithubAuth = (options: UseGithubAuthOptions = {}): UseGithubAuthReturn => {
  const { isLoading, error, start, complete } = useOAuthLogin(options);
  const startGithubAuth = useCallback(() => start('github'), [start]);
  const handleGithubCallback = useCallback(
    (code: string, state: string) => complete('github', code, state),
    [complete],
  );
  return { isLoading, error, startGithubAuth, handleGithubCallback };
};
