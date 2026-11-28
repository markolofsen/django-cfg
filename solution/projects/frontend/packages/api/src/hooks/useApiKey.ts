'use client';

import { useCallback, useEffect, useState } from 'react';

import {
  cfgAccountsApiKeyRegenerateCreate,
  cfgAccountsApiKeyRetrieve,
  cfgAccountsApiKeyRevealCreate,
  cfgAccountsApiKeyTestCreate,
} from '../_api/endpoints';
import type { APIKey } from '../_api/models';

export interface ApiKeyTestResult {
  valid: boolean;
  userId: string | null;
}

export interface UseApiKeyReturn {
  apiKey: string | null;
  isRevealed: boolean;
  reissuedAt: string | null;
  createdAt: string | null;
  isLoading: boolean;
  isRevealing: boolean;
  isRegenerating: boolean;
  isTesting: boolean;
  reveal: (options?: { show?: boolean }) => Promise<string | null>;
  regenerate: () => Promise<void>;
  testKey: (key: string) => Promise<ApiKeyTestResult>;
  refresh: () => void;
}

export function useApiKey(): UseApiKeyReturn {
  const [data, setData] = useState<APIKey | null>(null);
  const [freshKey, setFreshKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRevealing, setIsRevealing] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isTesting, setIsTesting] = useState(false);

  const refresh = useCallback(() => {
    setFreshKey(null);
    setIsLoading(true);
    void cfgAccountsApiKeyRetrieve()
      .then(setData)
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const reveal = useCallback(async (options?: { show?: boolean }) => {
    setIsRevealing(true);
    try {
      const result = await cfgAccountsApiKeyRevealCreate({});
      const fullKey = result.key ?? null;
      if (fullKey && options?.show !== false) setFreshKey(fullKey);
      return fullKey;
    } finally {
      setIsRevealing(false);
    }
  }, []);

  const regenerate = useCallback(async () => {
    setIsRegenerating(true);
    try {
      const result = await cfgAccountsApiKeyRegenerateCreate({});
      setFreshKey(result.key ?? null);
      setData((current) => current ? { ...current, ...result } : current);
    } finally {
      setIsRegenerating(false);
    }
  }, []);

  const testKey = useCallback(async (key: string): Promise<ApiKeyTestResult> => {
    setIsTesting(true);
    try {
      const result = await cfgAccountsApiKeyTestCreate({ key });
      return { valid: Boolean(result.valid), userId: result.user_id ?? null };
    } finally {
      setIsTesting(false);
    }
  }, []);

  return {
    apiKey: freshKey ?? data?.key ?? null,
    isRevealed: freshKey !== null,
    reissuedAt: data?.reissued_at ?? null,
    createdAt: data?.created_at ?? null,
    isLoading,
    isRevealing,
    isRegenerating,
    isTesting,
    reveal,
    regenerate,
    testKey,
    refresh,
  };
}
