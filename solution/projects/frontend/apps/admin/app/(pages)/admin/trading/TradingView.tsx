'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from '@djangocfg/ui';
import { Plus, RefreshCw } from 'lucide-react';
import { useTrading } from '@/contexts';
import { PortfolioStats, OrderCard, CreateOrderDialog } from './components';
import { openCreateOrderDialog } from './events';

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

  if (portfolioLoading || ordersLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-muted rounded" />
          <div className="grid gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
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
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Trading</h1>
            <p className="text-muted-foreground mt-2">
              Manage your trading portfolio and orders
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refreshPortfolio();
                refreshOrders();
              }}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button size="sm" onClick={() => openCreateOrderDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              New Order
            </Button>
          </div>
        </div>

        {/* Portfolio Stats */}
        <PortfolioStats portfolio={portfolio} stats={portfolioStats} />

        {/* Orders List */}
        <Card>
          <CardHeader>
            <CardTitle>Active Orders</CardTitle>
            <CardDescription>
              Your current trading orders
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {orders.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No orders yet. Create your first order to get started.
              </div>
            ) : (
              orders.map((order) => (
                <OrderCard key={order.id} order={order} onCancel={cancelOrder} />
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dialogs */}
      <CreateOrderDialog />
    </>
  );
}
