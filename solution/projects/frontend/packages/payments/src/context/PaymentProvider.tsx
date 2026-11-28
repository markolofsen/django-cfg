'use client';

// ============================================================================
// @djangocfg/payments — PaymentProvider context (the injected transport seam)
// ============================================================================
// The host picks ONE adapter (mock or stripe) and injects it here. Package
// hooks/components read it via usePaymentAdapter() — they never import a
// concrete SDK or a generated client.

import React, { createContext, useContext } from 'react';
import type { PaymentProviderAdapter } from '../domain/types';

const PaymentAdapterContext = createContext<PaymentProviderAdapter | null>(null);

export interface PaymentProviderProps {
  adapter: PaymentProviderAdapter;
  children: React.ReactNode;
}

export function PaymentProvider({ adapter, children }: PaymentProviderProps) {
  return (
    <PaymentAdapterContext.Provider value={adapter}>
      {children}
    </PaymentAdapterContext.Provider>
  );
}

/** Read the injected adapter. Throws if no <PaymentProvider> is mounted. */
export function usePaymentAdapter(): PaymentProviderAdapter {
  const adapter = useContext(PaymentAdapterContext);
  if (!adapter) {
    throw new Error(
      'usePaymentAdapter must be used within a <PaymentProvider adapter={…}>. ' +
        'Inject a mock or stripe adapter at the app root.',
    );
  }
  return adapter;
}
