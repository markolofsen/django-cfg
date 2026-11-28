'use client';

import { useCallback, useEffect, useState } from 'react';

import { useApiKey } from '@djangocfg/api/hooks';
import { useCallbackRef } from '@djangocfg/ui-core/hooks';

import type { Renewal } from '../../renew/McpRenew';
import type { KeyState } from './useMcpKey';

/**
 * The signed-in user's django-cfg API key, through `@djangocfg/api`'s `useApiKey` (the generated `cfg/accounts/api-key` hooks, on the
 * host's configured client and auth): `reveal` once per user, `regenerate` for "Renew access". The key is durable and revealable, so
 * nothing here is "shown once". Mount with `key={userId}` so a user change starts clean.
 */
export function useCfgKey() {
  const api = useApiKey();
  const reveal = useCallbackRef(api.reveal);
  const regenerate = useCallbackRef(api.regenerate);
  const [phase, setPhase] = useState<'loading' | 'done' | 'error'>('loading');
  const [attempt, setAttempt] = useState(0);
  /* `useApiKey` reads "last reissued" from a request made before the renewal; the renewal's own moment is newer. */
  const [renewedAt, setRenewedAt] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    setPhase('loading');
    reveal().then(
      () => live && setPhase('done'),
      () => live && setPhase('error'),
    );
    return () => {
      live = false;
    };
  }, [reveal, attempt]);

  const state: KeyState =
    phase === 'loading' ? { kind: 'loading' } : phase === 'error' ? { kind: 'error' } : api.isRevealed && api.apiKey ? { kind: 'ready', key: api.apiKey } : { kind: 'missing' };

  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  const renewal: Renewal = {
    reissuedAt: renewedAt ?? api.reissuedAt,
    run: async () => {
      await regenerate();
      setRenewedAt(new Date().toISOString());
    },
  };
  return { state, retry, renewal };
}
