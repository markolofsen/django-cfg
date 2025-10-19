'use client';

import React, { createContext, useContext, type ReactNode } from 'react';

// ─────────────────────────────────────────────────────────────────────────
// NOTE: API Keys feature has been removed in Payments v2.0
// This context is kept as a stub for backward compatibility
// ─────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface ApiKeysContextValue {
  // Deprecated - returns empty data
  apiKeys: undefined;
  isLoadingApiKeys: boolean;
  apiKeysError: Error | undefined;
  refreshApiKeys: () => Promise<void>;

  // Deprecated operations - throw errors
  getApiKey: (id: string) => Promise<never>;
  createApiKey: (data: any) => Promise<never>;
  deleteApiKey: (id: string) => Promise<never>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const ApiKeysContext = createContext<ApiKeysContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function ApiKeysProvider({ children }: { children: ReactNode }) {
  const refreshApiKeys = async () => {
    // No-op - feature deprecated
  };

  const getApiKey = async (id: string): Promise<never> => {
    throw new Error('API Keys feature has been removed in Payments v2.0');
  };

  const createApiKey = async (data: any): Promise<never> => {
    throw new Error('API Keys feature has been removed in Payments v2.0');
  };

  const deleteApiKey = async (id: string): Promise<never> => {
    throw new Error('API Keys feature has been removed in Payments v2.0');
  };

  const value: ApiKeysContextValue = {
    apiKeys: undefined,
    isLoadingApiKeys: false,
    apiKeysError: undefined,
    refreshApiKeys,
    getApiKey,
    createApiKey,
    deleteApiKey,
  };

  return <ApiKeysContext.Provider value={value}>{children}</ApiKeysContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useApiKeysContext(): ApiKeysContextValue {
  const context = useContext(ApiKeysContext);
  if (!context) {
    throw new Error('useApiKeysContext must be used within ApiKeysProvider');
  }
  return context;
}

