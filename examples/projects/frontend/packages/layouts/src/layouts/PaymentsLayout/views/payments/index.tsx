/**
 * Payments View (v2.0 - Simplified)
 * List and manage payment transactions
 */

'use client';

import React from 'react';
import { PaymentsList } from './components';

export const PaymentsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <PaymentsList />
    </div>
  );
};
