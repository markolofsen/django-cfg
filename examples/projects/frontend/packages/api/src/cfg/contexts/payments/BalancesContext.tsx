'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  usePaymentsBalanceRetrieve,
} from '../../generated/_utils/hooks';
import type { API } from '../../generated';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface BalancesContextValue {
  // Balance data - single endpoint returns balance info
  balance: any | undefined;
  isLoadingBalance: boolean;
  balanceError: Error | undefined;
  refreshBalance: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const BalancesContext = createContext<BalancesContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function BalancesProvider({ children }: { children: ReactNode }) {
  // Get balance from /cfg/payments/balance/
  const {
    data: balance,
    error: balanceError,
    isLoading: isLoadingBalance,
    mutate: mutateBalance,
  } = usePaymentsBalanceRetrieve(api as unknown as API);

  const refreshBalance = async () => {
    await mutateBalance();
  };

  const value: BalancesContextValue = {
    balance,
    isLoadingBalance,
    balanceError,
    refreshBalance,
  };

  return <BalancesContext.Provider value={value}>{children}</BalancesContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useBalancesContext(): BalancesContextValue {
  const context = useContext(BalancesContext);
  if (!context) {
    throw new Error('useBalancesContext must be used within BalancesProvider');
  }
  return context;
}
