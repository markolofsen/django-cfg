'use client';

import { useCallback, useEffect, useState } from 'react';

import { useCallbackRef } from '@djangocfg/ui-core/hooks';

export type KeyState =
  | { kind: 'loading' }
  | { kind: 'ready'; key: string }
  | { kind: 'missing' }
  | { kind: 'error' };

/**
 * Resolves the signed-in user's MCP key: a key string, null when the account
 * has none, or a throw on failure. The host owns it, because where keys live
 * (and their shape) is the project's, not django-cfg's.
 */
/**
 * Mints a key and returns its secret, for hosts that store only a hash (the secret exists once, so `loadKey` cannot return it later).
 * Throwing shows the error bar.
 */
export type McpKeyCreator = (request: { token: string | null; signal: AbortSignal }) => Promise<string>;

export type McpKeyLoader = (request: { token: string | null; signal: AbortSignal }) => Promise<string | null>;

/** One load per signed-in user, plus retry. Nothing is stored. */
export function useMcpKey({
  loadKey,
  userId,
  getToken,
}: {
  loadKey: McpKeyLoader;
  /** Reload when the signed-in user changes. */
  userId: string;
  getToken: () => string | null;
}) {
  const [state, setState] = useState<KeyState>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  const token = useCallbackRef(getToken);
  const load = useCallbackRef(loadKey);

  useEffect(() => {
    const abort = new AbortController();
    setState({ kind: 'loading' });
    load({ token: token(), signal: abort.signal })
      .then((key) => {
        if (!abort.signal.aborted) setState(key ? { kind: 'ready', key } : { kind: 'missing' });
      })
      .catch(() => {
        if (!abort.signal.aborted) setState({ kind: 'error' });
      });
    return () => abort.abort();
  }, [userId, token, load, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  const setKey = useCallback((key: string) => setState({ kind: 'ready', key }), []);
  return { state, retry, setKey };
}
