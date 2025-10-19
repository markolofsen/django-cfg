/**
 * Balance Card Component (v2.0 - Simplified)
 * Display user balance with quick actions
 */

'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Skeleton,
} from '@djangocfg/ui';
import { Wallet, RefreshCw, Plus } from 'lucide-react';
import { useOverviewContext } from '@djangocfg/api/cfg/contexts';
import { openCreatePaymentDialog } from '../../../events';

export const BalanceCard: React.FC = () => {
  const {
    balance,
    isLoadingBalance,
    refreshBalance
  } = useOverviewContext();

  const formatCurrency = (amount?: number | null) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'No transactions yet';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'Invalid date';
    }
  };

  if (isLoadingBalance) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              Account Balance
            </div>
            <Skeleton className="h-8 w-20" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardContent>
      </Card>
    );
  }

  // Extract balance data from response: { success, balance: { amount_usd, total_deposited, total_withdrawn, last_transaction_at } }
  const balanceData = balance?.balance || balance;
  const amountUsd = balanceData?.amount_usd ?? 0;
  const totalDeposited = balanceData?.total_deposited ?? 0;
  const totalWithdrawn = balanceData?.total_withdrawn ?? 0;
  const lastTransactionAt = balanceData?.last_transaction_at;
  const isEmpty = amountUsd === 0 && totalDeposited === 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Account Balance
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={refreshBalance}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button size="sm" onClick={() => openCreatePaymentDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              Add Funds
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="text-4xl font-bold">
            {formatCurrency(amountUsd)}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Available balance • Last updated {formatDate(lastTransactionAt)}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <p className="text-xs text-muted-foreground">Total Deposited</p>
            <p className="text-lg font-semibold text-green-600">{formatCurrency(totalDeposited)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Withdrawn</p>
            <p className="text-lg font-semibold text-red-600">{formatCurrency(totalWithdrawn)}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant={!isEmpty ? 'default' : 'secondary'}>
            {!isEmpty ? 'Active' : 'New Account'}
          </Badge>
          {isEmpty && <Badge variant="outline">Empty Balance</Badge>}
        </div>
      </CardContent>
    </Card>
  );
};
