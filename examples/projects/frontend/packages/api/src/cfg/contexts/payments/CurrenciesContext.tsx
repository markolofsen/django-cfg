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

export interface CurrenciesContextValue {
  // Currencies data - returns raw response with currencies array
  currencies: any | undefined;
  isLoadingCurrencies: boolean;
  currenciesError: Error | undefined;
  refreshCurrencies: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const CurrenciesContext = createContext<CurrenciesContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function CurrenciesProvider({ children }: { children: ReactNode }) {
  // Get currencies list from /cfg/payments/currencies/
  const {
    data: currencies,
    error: currenciesError,
    isLoading: isLoadingCurrencies,
    mutate: mutateCurrencies,
  } = usePaymentsCurrenciesList(api as unknown as API);

  const refreshCurrencies = async () => {
    await mutateCurrencies();
  };

  const value: CurrenciesContextValue = {
    currencies,
    isLoadingCurrencies,
    currenciesError,
    refreshCurrencies,
  };

  return <CurrenciesContext.Provider value={value}>{children}</CurrenciesContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useCurrenciesContext(): CurrenciesContextValue {
  const context = useContext(CurrenciesContext);
  if (!context) {
    throw new Error('useCurrenciesContext must be used within CurrenciesProvider');
  }
  return context;
}

