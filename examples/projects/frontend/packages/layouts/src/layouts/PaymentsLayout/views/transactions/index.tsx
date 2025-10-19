/**
 * Transactions View (v2.0 - Simplified)
 * View transaction history and balance changes
 */

'use client';

import React from 'react';
import { TransactionsList } from './components';

export const TransactionsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <TransactionsList />
    </div>
  );
};
