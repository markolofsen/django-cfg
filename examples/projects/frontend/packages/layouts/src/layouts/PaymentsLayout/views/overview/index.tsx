/**
 * Overview View (v2.0 - Simplified)
 * Dashboard with balance and recent payments
 */

'use client';

import React from 'react';
import { BalanceCard, RecentPayments } from './components';

export const OverviewView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <BalanceCard />
        <RecentPayments />
      </div>
    </div>
  );
};
