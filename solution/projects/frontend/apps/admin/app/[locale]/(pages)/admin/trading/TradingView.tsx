'use client';

import { Plus, RefreshCw } from 'lucide-react';

import { useTrading } from '@/contexts';
import {
    Button, Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@djangocfg/ui-nextjs';

import { CreateOrderDialog, OrderCard, PortfolioStats } from './components';
import { openCreateOrderDialog } from './events';

const SKELETON_ITEMS = [0, 1, 2, 3];

export function TradingView() {
  const {
    portfolio,
    portfolioStats,
    portfolioLoading,
    orders,
    ordersLoading,
    cancelOrder,
    refreshPortfolio,
    refreshOrders
  } = useTrading();

  const isLoading = portfolioLoading || ordersLoading;
  const hasOrders = orders.length > 0;

  const handleRefresh = () => {
    refreshPortfolio();
    refreshOrders();
  };

  const handleNewOrder = () => openCreateOrderDialog();

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-muted rounded" />
          <div className="grid gap-4 md:grid-cols-4">
            {SKELETON_ITEMS.map((i) => (
              <div key={i} className="h-32 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Trading</h1>
            <p className="text-muted-foreground mt-2">
              Manage your trading portfolio and orders
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button size="sm" onClick={handleNewOrder}>
              <Plus className="h-4 w-4 mr-2" />
              New Order
            </Button>
          </div>
        </div>

        {/* Portfolio Stats */}
        <PortfolioStats portfolio={portfolio} stats={portfolioStats} />

        <Card>
          <CardHeader>
            <CardTitle>Active Orders</CardTitle>
            <CardDescription>Your current trading orders</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {hasOrders ? (
              orders.map((order) => (
                <OrderCard key={order.id} order={order} onCancel={cancelOrder} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No orders yet. Create your first order to get started.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dialogs */}
      <CreateOrderDialog />
    </>
  );
}
