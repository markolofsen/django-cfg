'use client';

import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

import { useApiKey } from '@djangocfg/api/hooks';
import { toast } from '@djangocfg/ui-core/hooks';

import { useSettingsCopy, type SettingsCopy } from '../../i18n';

export type ApiKeyLabels = SettingsCopy['apiKey'];

// ─────────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────────

interface ApiKeyContextValue {
  labels: ApiKeyLabels;
  apiKey: string | null;
  reissuedAt: string | null;
  createdAt: string | null;
  isLoading: boolean;
  error: string | null;
  isArmed: boolean;
  arm: () => void;
  disarm: () => void;
  regenerate: () => Promise<void>;
  isRegenerating: boolean;
  isFresh: boolean;
  dismissFresh: () => void;
  /** The full key for the clipboard: the one on screen when it is already full, else fetched (not rotated, not shown). `null` if it could not be read. */
  fullKey: () => Promise<string | null>;
  testKey: () => Promise<void>;
  isTesting: boolean;
  testResult: boolean | null;
}

const ApiKeyContext = createContext<ApiKeyContextValue | null>(null);

export const useApiKeyContext = (): ApiKeyContextValue => {
  const ctx = useContext(ApiKeyContext);
  if (!ctx) throw new Error('useApiKeyContext must be used within ApiKeyProvider');
  return ctx;
};

// ─────────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────────

export const ApiKeyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { apiKey, reissuedAt, createdAt, isLoading, isRegenerating, isTesting, regenerate, testKey, refresh, reveal } = useApiKey();

  const LABELS = useSettingsCopy().apiKey;
  const [isArmed, setIsArmed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<boolean | null>(null);

  const arm = useCallback(() => { setError(null); setIsArmed(true); }, []);
  const disarm = useCallback(() => setIsArmed(false), []);

  // Detect when the key is "fresh" (full key shown once after regenerate).
  // Backend GET returns masked keys (contain •). If no •, it's the fresh full key.
  const isFresh = apiKey ? !apiKey.includes('•') : false;

  const dismissFresh = useCallback(() => {
    refresh();
  }, [refresh]);

  const fullKey = useCallback(async () => {
    if (apiKey && isFresh) return apiKey;
    try {
      return await reveal({ show: false });
    } catch {
      return null;
    }
  }, [apiKey, isFresh, reveal]);

  const handleRegenerate = useCallback(async () => {
    try {
      setError(null);
      await regenerate();
      setIsArmed(false);
      setTestResult(null);
      toast.success(LABELS.regenerated);
    } catch {
      setError(LABELS.failedToRegenerate);
      toast.error(LABELS.failedToRegenerate);
    }
  }, [regenerate, LABELS]);

  const handleTest = useCallback(async () => {
    if (!apiKey) return;
    setTestResult(null);
    try {
      const result = await testKey(apiKey);
      setTestResult(result.valid);
      if (result.valid) {
        toast.success(LABELS.testSuccess);
      } else {
        toast.error(LABELS.testFailed);
      }
    } catch {
      setTestResult(false);
      toast.error(LABELS.testFailed);
    }
  }, [apiKey, testKey, LABELS]);

  const value = useMemo<ApiKeyContextValue>(() => ({
    labels: LABELS,
    apiKey,
    reissuedAt,
    createdAt,
    isLoading,
    error,
    isArmed,
    arm,
    disarm,
    regenerate: handleRegenerate,
    isRegenerating,
    isFresh,
    dismissFresh,
    fullKey,
    testKey: handleTest,
    isTesting,
    testResult,
  }), [
    LABELS, apiKey, reissuedAt, createdAt, isLoading, error,
    isArmed, arm, disarm, handleRegenerate, isRegenerating, isFresh, dismissFresh,
    fullKey, handleTest, isTesting, testResult,
  ]);

  return (
    <ApiKeyContext.Provider value={value}>
      {children}
    </ApiKeyContext.Provider>
  );
};
