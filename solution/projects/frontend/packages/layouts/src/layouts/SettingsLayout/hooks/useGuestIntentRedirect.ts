'use client';

/**
 * useGuestIntentRedirect — a guest who arrives on `#settings/<section>?<intent>` is sent to sign-in and brought back.
 *
 * The dialog only opens for a signed-in user, so without this an assistant's consent link (`#settings/mcp?request=…`)
 * lands on a page where nothing happens. The full address, fragment included, is saved as the post-sign-in
 * destination, so the dialog reads the same intent once the session exists. A plain `#settings` (no intent) is left
 * alone: a guest opening it has nothing pending.
 */

import { useEffect, useRef } from 'react';

import { useAuth, useCfgRouter } from '@djangocfg/api/auth';

import { carriesIntent } from '../intent/parseSettingsHash';

export function useGuestIntentRedirect(urlKey: string, enabled: boolean): void {
  const { isAuthenticated, isLoading, saveRedirectUrl, routes } = useAuth();
  const router = useCfgRouter();
  const sent = useRef(false);

  useEffect(() => {
    if (!enabled || isLoading || isAuthenticated || sent.current) return;
    if (!carriesIntent(window.location.hash.slice(1), urlKey)) return;
    sent.current = true;
    const { pathname, search, hash } = window.location;
    saveRedirectUrl(`${pathname}${search}${hash}`);
    router.push(routes.auth);
  }, [enabled, isLoading, isAuthenticated, saveRedirectUrl, router, routes.auth, urlKey]);
}
