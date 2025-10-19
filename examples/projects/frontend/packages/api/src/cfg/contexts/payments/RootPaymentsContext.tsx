'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  usePaymentsCurrenciesList,
} from '../../generated/_utils/hooks';
import type { API } from '../../generated';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface RootPaymentsContextValue {
  // Currencies - simplified to single endpoint
  currencies: any | undefined;
  isLoadingCurrencies: boolean;
  currenciesError: Error | undefined;
  refreshCurrencies: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const RootPaymentsContext = createContext<RootPaymentsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function RootPaymentsProvider({ children }: { children: ReactNode }) {
  // Get currencies list from /cfg/payments/currencies/
  // In v2.0, this returns all currencies with network info embedded
  const {
    data: currencies,
    error: currenciesError,
    isLoading: isLoadingCurrencies,
    mutate: mutateCurrencies,
  } = usePaymentsCurrenciesList(api as unknown as API);

  const refreshCurrencies = async () => {
    await mutateCurrencies();
  };

  const value: RootPaymentsContextValue = {
    currencies,
    isLoadingCurrencies,
    currenciesError,
    refreshCurrencies,
  };

  return (
    <RootPaymentsContext.Provider value={value}>{children}</RootPaymentsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useRootPaymentsContext(): RootPaymentsContextValue {
  const context = useContext(RootPaymentsContext);
  if (!context) {
    throw new Error('useRootPaymentsContext must be used within RootPaymentsProvider');
  }
  return context;
}
