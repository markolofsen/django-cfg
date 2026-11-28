/**
 * The private landing route AppLayout/BaseApp configures: `auth.routes.defaultCallback`, resolved by the auth
 * provider (default `/private`). Returns `undefined` outside the provider, so stories and tests fall back to `/`.
 * Reads the context directly: `useAuth()` returns default state outside the provider, which would leak the
 * framework default.
 */

'use client';

import { useContext } from 'react';

import { AuthContext } from '@djangocfg/api/auth';

export function useLandingRoute(): string | undefined {
  return useContext(AuthContext)?.routes?.defaultCallback || undefined;
}
