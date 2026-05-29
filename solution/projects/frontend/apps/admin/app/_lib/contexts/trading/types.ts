/**
 * Trading Context Types
 * Single source of truth for trading-related types
 */

import type {
  Portfolio,
  PortfolioStats,
  Order,
  OrderCreateRequest,
} from '../../api/generated/_trading';

// Re-export schema types from generated API
export type { Portfolio, PortfolioStats, Order, OrderCreateRequest };

// Context state types
export interface TradingContextType {
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
