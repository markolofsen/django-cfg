'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { SWRConfig } from 'swr';
import { api } from '../../BaseClient';
import {
  usePaymentsBalanceRetrieve,
  usePaymentsPaymentsList,
  usePaymentsTransactionsList,
  useCreatePaymentsPaymentsCreateCreate,
} from '../../generated/_utils/hooks';
import type { API } from '../../generated';
import type {
  PaginatedPaymentListList,
  PaymentList,
} from '../../generated/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface OverviewContextValue {
  // Balance data
  balance: any | undefined;
  isLoadingBalance: boolean;
  balanceError: Error | undefined;
  refreshBalance: () => Promise<void>;

  // Payments data
  payments: PaginatedPaymentListList | undefined;
  isLoadingPayments: boolean;
  paymentsError: Error | undefined;
  refreshPayments: () => Promise<void>;

  // Transactions data
  transactions: any | undefined;
  isLoadingTransactions: boolean;
  transactionsError: Error | undefined;
  refreshTransactions: () => Promise<void>;

  // Payment operations
  createPayment: () => Promise<PaymentList>;

  // Loading states
  isLoadingOverview: boolean;
  overviewError: Error | undefined;

  // Operations
  refreshOverview: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const OverviewContext = createContext<OverviewContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function OverviewProvider({ children }: { children: ReactNode }) {
  // SWR config for overview data - disable auto-revalidation
  const swrConfig = {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    revalidateIfStale: false,
  };

  // Balance
  const {
    data: balance,
    error: balanceError,
    isLoading: isLoadingBalance,
    mutate: mutateBalance,
  } = usePaymentsBalanceRetrieve(api as unknown as API);

  // Payments list
  const {
    data: payments,
    error: paymentsError,
    isLoading: isLoadingPayments,
    mutate: mutatePayments,
  } = usePaymentsPaymentsList({}, api as unknown as API);

  // Transactions
  const {
    data: transactions,
    error: transactionsError,
    isLoading: isLoadingTransactions,
    mutate: mutateTransactions,
  } = usePaymentsTransactionsList({}, api as unknown as API);

  // Payment mutations
  const createPaymentMutation = useCreatePaymentsPaymentsCreateCreate();

  const isLoadingOverview = isLoadingBalance || isLoadingPayments || isLoadingTransactions;
  const overviewError = balanceError || paymentsError || transactionsError;

  const refreshBalance = async () => {
    await mutateBalance();
  };

  const refreshPayments = async () => {
    await mutatePayments();
  };

  const refreshTransactions = async () => {
    await mutateTransactions();
  };

  const refreshOverview = async () => {
    await Promise.all([
      mutateBalance(),
      mutatePayments(),
      mutateTransactions(),
    ]);
  };

  // Create payment
  const createPayment = async (): Promise<PaymentList> => {
    const result = await createPaymentMutation(api as unknown as API);
    // Refresh overview data to show new payment
    await refreshOverview();
    return result as PaymentList;
  };

  const value: OverviewContextValue = {
    balance,
    isLoadingBalance,
    balanceError,
    refreshBalance,
    payments,
    isLoadingPayments,
    paymentsError,
    refreshPayments,
    transactions,
    isLoadingTransactions,
    transactionsError,
    refreshTransactions,
    createPayment,
    isLoadingOverview,
    overviewError,
    refreshOverview,
  };

  return (
    <SWRConfig value={swrConfig}>
      <OverviewContext.Provider value={value}>{children}</OverviewContext.Provider>
    </SWRConfig>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useOverviewContext(): OverviewContextValue {
  const context = useContext(OverviewContext);
  if (!context) {
    throw new Error('useOverviewContext must be used within OverviewProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  PaginatedPaymentListList,
  PaymentList,
};

