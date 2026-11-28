'use client';

import { useEffect, useMemo, useState, useSyncExternalStore } from 'react';

import { cfgAccountsOauthProvidersRetrieve } from '../../_api/endpoints';
import { CFG_KEYS, cfgStorage } from '../../runtime/keys';
import type { OAuthProviderInfo } from '../../_api/models';
import { OAUTH_PROVIDER_IDS } from './useOAuthLogin';

export interface UseOAuthProvidersReturn {
  /** Providers the server has configured, in the server's display order. Empty until ready and on failure. */
  providers: OAuthProviderInfo[];
  /** False only while the first request is in flight and nothing is cached. */
  isReady: boolean;
}

const EMPTY: OAuthProviderInfo[] = [];
const CACHE_KEY = CFG_KEYS.oauthProviders.key;

/** A failed request is tried again this many times before the list is given up as empty. */
export const OAUTH_PROVIDERS_MAX_RETRIES = 2;
/** Base wait before a retry; grows linearly (1s, then 2s), so a flaky mobile network has ~3s to recover. */
export const OAUTH_PROVIDERS_RETRY_MS = 1000;

const isInfo = (value: unknown): value is OAuthProviderInfo =>
  typeof value === 'object' && value !== null && typeof (value as { id?: unknown }).id === 'string';

// useSyncExternalStore needs a stable snapshot: parse again only when the stored text changed.
let lastRaw: string | null = null;
let lastParsed: OAuthProviderInfo[] | undefined;

/** The list the previous page of this tab fetched; `undefined` when none or unreadable. */
const readCached = (): OAuthProviderInfo[] | undefined => {
  const raw = cfgStorage.read(CACHE_KEY);
  if (raw === lastRaw) return lastParsed;
  lastRaw = raw;
  try {
    const parsed: unknown = raw === null ? null : JSON.parse(raw);
    lastParsed = Array.isArray(parsed) && parsed.every(isInfo) ? parsed : undefined;
  } catch {
    lastParsed = undefined;
  }
  return lastParsed;
};

const subscribe = () => () => {};
const serverSnapshot = () => undefined;

/**
 * The sign-in providers the server offers (`GET /cfg/accounts/oauth/providers/`).
 *
 * Fetched once per page session and kept in `sessionStorage`, so a reload or
 * "Try again" after a failed callback shows the buttons at once; the server
 * answer always wins. A failed request is retried twice (a dropped mobile
 * connection or a gateway 502 must not hide the buttons for the whole visit);
 * only when the retries fail too does the hook yield the cached list, else
 * `[]`, with `isReady: true`: the email form never waits on, or breaks
 * because of, this list. Ids this client has no adapter for (a newer backend) are dropped.
 */
export const useOAuthProviders = (): UseOAuthProvidersReturn => {
  // Server and first client render see `undefined`, so hydration matches.
  const cached = useSyncExternalStore(subscribe, readCached, serverSnapshot);

  const [failed, setFailed] = useState(false);

  const [data, setData] = useState<{ providers: OAuthProviderInfo[] } | undefined>(
    cached ? { providers: cached } : undefined,
  );

  useEffect(() => {
    let cancelled = false;
    const load = async (attempt = 0): Promise<void> => {
      try {
        const response = await cfgAccountsOauthProvidersRetrieve();
        if (cancelled) return;
        setFailed(false);
        setData(response);
        cfgStorage.writeJSON(CACHE_KEY, response.providers);
      } catch {
        if (cancelled) return;
        if (attempt < OAUTH_PROVIDERS_MAX_RETRIES) {
          window.setTimeout(() => void load(attempt + 1), OAUTH_PROVIDERS_RETRY_MS * (attempt + 1));
        } else {
          setFailed(true);
        }
      }
    };
    void load();
    return () => { cancelled = true; };
  }, []);

  const providers = useMemo(
    () => data?.providers.filter((p) => OAUTH_PROVIDER_IDS.includes(p.id)) ?? EMPTY,
    [data],
  );

  // Ready on an answer, on a cached list (usable at once), or when the retries gave up.
  // Not `isLoading`: it is off in the wait between a failure and its retry.
  return { providers, isReady: data !== undefined || failed || cached !== undefined };
};
