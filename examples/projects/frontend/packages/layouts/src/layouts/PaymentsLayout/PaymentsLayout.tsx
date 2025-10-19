/**
 * Payments Layout (v2.0 - Simplified)
 *
 * Simplified layout with 3 tabs: Overview, Payments, Transactions
 * Removed: API Keys, Tariffs (deprecated in v2.0)
 */

'use client';

import React from 'react';
import {
  PaymentsProvider,
  OverviewProvider,
  RootPaymentsProvider,
} from '@djangocfg/api/cfg/contexts';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';
import { Wallet, CreditCard, History } from 'lucide-react';
import { OverviewView } from './views/overview';
import { PaymentsView } from './views/payments';
import { TransactionsView } from './views/transactions';
import { CreatePaymentDialog, PaymentDetailsDialog } from './components';

// ─────────────────────────────────────────────────────────────────────────
// Payments Layout
// ─────────────────────────────────────────────────────────────────────────

export interface PaymentsLayoutProps {
  children?: React.ReactNode;
}

export const PaymentsLayout: React.FC<PaymentsLayoutProps> = () => {
  return (
    <RootPaymentsProvider>
      <div className="h-full p-6 space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Payments</h1>
          <p className="text-muted-foreground">
            Manage your payments, balance, and transaction history
          </p>
        </div>

        {/* Main Content with Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground">
            <TabsTrigger value="overview" className="inline-flex items-center gap-2 px-3 py-1.5">
              <Wallet className="h-4 w-4" />
              <span className="hidden sm:inline">Overview</span>
            </TabsTrigger>
            <TabsTrigger value="payments" className="inline-flex items-center gap-2 px-3 py-1.5">
              <CreditCard className="h-4 w-4" />
              <span className="hidden sm:inline">Payments</span>
            </TabsTrigger>
            <TabsTrigger value="transactions" className="inline-flex items-center gap-2 px-3 py-1.5">
              <History className="h-4 w-4" />
              <span className="hidden sm:inline">Transactions</span>
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab - Balance + Recent Payments */}
          <TabsContent value="overview" className="space-y-6">
            <OverviewProvider>
              <PaymentsProvider>
                <OverviewView />
                <CreatePaymentDialog />
              </PaymentsProvider>
            </OverviewProvider>
          </TabsContent>

          {/* Payments Tab - Full Payment List */}
          <TabsContent value="payments" className="space-y-6">
            <PaymentsProvider>
              <PaymentsView />
              <CreatePaymentDialog />
            </PaymentsProvider>
          </TabsContent>

          {/* Transactions Tab - Transaction History */}
          <TabsContent value="transactions" className="space-y-6">
            <OverviewProvider>
              <TransactionsView />
            </OverviewProvider>
          </TabsContent>
        </Tabs>

        {/* Global Payment Details Dialog */}
        <PaymentDetailsDialog />
      </div>
    </RootPaymentsProvider>
  );
};
