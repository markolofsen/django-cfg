'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  usePaymentsPaymentsList,
  usePaymentsPaymentsRetrieve,
  useCreatePaymentsPaymentsCreateCreate,
  useCreatePaymentsPaymentsConfirmCreate,
  usePaymentsPaymentsStatusRetrieve,
} from '../../generated/_utils/hooks';
import { getPaymentsPaymentsRetrieve } from '../../generated/_utils/fetchers';
import { defaultLogger } from '../../generated/logger';
import type { API } from '../../generated';
import type {
  PaginatedPaymentListList,
  PaymentDetail,
  PaymentList,
} from '../../generated/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface PaymentsContextValue {
  // List
  payments: PaginatedPaymentListList | undefined;
  isLoadingPayments: boolean;
  paymentsError: Error | undefined;
  refreshPayments: () => Promise<void>;

  // Operations
  getPayment: (id: string) => Promise<PaymentDetail | undefined>;
  createPayment: () => Promise<PaymentList>;
  confirmPayment: (id: string) => Promise<PaymentList>;
  checkPaymentStatus: (id: string) => Promise<PaymentList | undefined>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const PaymentsContext = createContext<PaymentsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function PaymentsProvider({ children }: { children: ReactNode }) {
  // List payments
  const {
    data: payments,
    error: paymentsError,
    isLoading: isLoadingPayments,
    mutate: mutatePayments,
  } = usePaymentsPaymentsList({}, api as unknown as API);

  const refreshPayments = async () => {
    await mutatePayments();
  };

  // Mutations
  const createPaymentMutation = useCreatePaymentsPaymentsCreateCreate();
  const confirmPaymentMutation = useCreatePaymentsPaymentsConfirmCreate();

  // Get single payment
  const getPayment = async (id: string): Promise<PaymentDetail | undefined> => {
    try {
      const result = await getPaymentsPaymentsRetrieve(id, api as unknown as API);
      return result;
    } catch (error) {
      defaultLogger.error('Failed to retrieve payment:', error);
      return undefined;
    }
  };

  // Create payment
  const createPayment = async (): Promise<PaymentList> => {
    const result = await createPaymentMutation(api as unknown as API);
    await refreshPayments();
    return result as PaymentList;
  };

  // Confirm payment (user clicked "I paid")
  const confirmPayment = async (id: string): Promise<PaymentList> => {
    const result = await confirmPaymentMutation(id, api as unknown as API);
    await refreshPayments();
    return result as PaymentList;
  };

  // Check payment status
  const checkPaymentStatus = async (id: string): Promise<PaymentList | undefined> => {
    const { data } = usePaymentsPaymentsStatusRetrieve(id, api as unknown as API);
    return data;
  };

  const value: PaymentsContextValue = {
    payments,
    isLoadingPayments,
    paymentsError,
    refreshPayments,
    getPayment,
    createPayment,
    confirmPayment,
    checkPaymentStatus,
  };

  return <PaymentsContext.Provider value={value}>{children}</PaymentsContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function usePaymentsContext(): PaymentsContextValue {
  const context = useContext(PaymentsContext);
  if (!context) {
    throw new Error('usePaymentsContext must be used within PaymentsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  PaginatedPaymentListList,
  PaymentDetail,
  PaymentList,
};

