/**
 * Trading Context
 *
 * Provides trading portfolio and orders management functionality.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { tradingClient } from '@/api/BaseClient';
import {
  useTradingPortfoliosMeRetrieve,
  useTradingPortfoliosStatsRetrieve,
  useTradingOrdersList,
  useCreateTradingOrdersCreate,
  useDeleteTradingOrdersDestroy
} from '../api/generated/trading/_utils/hooks/trading__api__trading';
import type { API } from '../api/generated/trading';
import type {
  Portfolio,
  PortfolioStats,
  Order,
  OrderCreateRequest
} from '../api/generated/trading/trading__api__trading/models';

interface TradingContextType {
  // Portfolio data
  portfolio: Portfolio | undefined;
  portfolioStats: PortfolioStats | undefined;
  portfolioLoading: boolean;
  portfolioError: Error | null;

  // Orders data
  orders: Order[];
  ordersLoading: boolean;
  ordersError: Error | null;

  // Actions
  createOrder: (data: OrderCreateRequest) => Promise<void>;
  cancelOrder: (orderId: number) => Promise<void>;
  refreshPortfolio: () => Promise<void>;
  refreshOrders: () => Promise<void>;
}

const TradingContext = createContext<TradingContextType | undefined>(undefined);

export function TradingProvider({ children }: { children: ReactNode }) {
  // Get current user's portfolio (SWR)
  const {
    data: portfolio,
    error: portfolioError,
    isLoading: portfolioLoading,
    mutate: mutatePortfolio
  } = useTradingPortfoliosMeRetrieve(tradingClient as unknown as API);

  // Get portfolio statistics (SWR)
  const {
    data: portfolioStats,
    isLoading: statsLoading,
  } = useTradingPortfoliosStatsRetrieve(tradingClient as unknown as API);

  // Get orders list (SWR)
  const {
    data: ordersData,
    error: ordersError,
    isLoading: ordersLoading,
    mutate: mutateOrders
  } = useTradingOrdersList({ page: 1, page_size: 100 }, tradingClient as unknown as API);

  // Mutation hooks
  const createOrderMutation = useCreateTradingOrdersCreate();
  const deleteOrderMutation = useDeleteTradingOrdersDestroy();

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
      await createOrderMutation(data, tradingClient as unknown as API);
      await mutateOrders();
      await mutatePortfolio();
    },
    cancelOrder: async (orderId: number) => {
      await deleteOrderMutation(orderId, tradingClient as unknown as API);
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
