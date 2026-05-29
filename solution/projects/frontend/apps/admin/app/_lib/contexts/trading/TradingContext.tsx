/**
 * Trading Context
 *
 * Provides trading portfolio and orders management functionality.
 */

import React, { createContext, ReactNode, useContext } from 'react';

import { tradingClient } from '@/api/BaseClient';

import {
    useTradingOrdersCreate, useTradingOrdersDestroy, useTradingOrdersList,
    useTradingPortfoliosMeRetrieve, useTradingPortfoliosStatsRetrieve
} from '../../api/generated/_trading/hooks';

import type { API } from '../../api/generated/_trading';
import type { OrderCreateRequest } from './types';
import type { TradingContextType } from './types';

const TradingContext = createContext<TradingContextType | undefined>(undefined);

export function TradingProvider({ children }: { children: ReactNode }) {
  // Get current user's portfolio (SWR)
  const {
    data: portfolio,
    error: portfolioError,
    isLoading: portfolioLoading,
    mutate: mutatePortfolio
  } = useTradingPortfoliosMeRetrieve();

  // Get portfolio statistics (SWR)
  const {
    data: portfolioStats,
    isLoading: statsLoading,
  } = useTradingPortfoliosStatsRetrieve();

  // Get orders list (SWR)
  const {
    data: ordersData,
    error: ordersError,
    isLoading: ordersLoading,
    mutate: mutateOrders
  } = useTradingOrdersList({ query: { page: 1, page_size: 100 } });

  // Mutation hooks
  const createOrderMutation = useTradingOrdersCreate();
  const deleteOrderMutation = useTradingOrdersDestroy();

  const orders = ordersData?.results || [];

  const value: TradingContextType = {
    portfolio,
    portfolioStats,
    portfolioLoading: portfolioLoading || statsLoading,
    portfolioError: portfolioError as Error | null,
    orders,
    ordersLoading,
    ordersError: ordersError as Error | null,
    createOrder: async (data: OrderCreateRequest) => {
      await createOrderMutation.trigger({ body: data });
      await mutateOrders();
      await mutatePortfolio();
    },
    cancelOrder: async (orderId: number) => {
      await deleteOrderMutation.trigger({ path: { id: orderId } });
      await mutateOrders();
      await mutatePortfolio();
    },
    refreshPortfolio: async () => {
      await mutatePortfolio();
    },
    refreshOrders: async () => {
      await mutateOrders();
    },
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
}

export function useTrading() {
  const context = useContext(TradingContext);
  if (context === undefined) {
    throw new Error('useTrading must be used within a TradingProvider');
  }
  return context;
}
