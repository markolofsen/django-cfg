/**
 * Trading Context Types
 * Single source of truth for trading-related types
 */

// Re-export schema types from generated API
export type {
  Portfolio,
  PortfolioStats,
  Order,
  OrderCreateRequest
} from '../../api/generated/trading/trading__api__trading/models';

// Context state types
export interface TradingContextType {
  // Portfolio data
  portfolio: import('../../api/generated/trading/trading__api__trading/models').Portfolio | undefined;
  portfolioStats: import('../../api/generated/trading/trading__api__trading/models').PortfolioStats | undefined;
  portfolioLoading: boolean;
  portfolioError: Error | null;

  // Orders data
  orders: import('../../api/generated/trading/trading__api__trading/models').Order[];
  ordersLoading: boolean;
  ordersError: Error | null;

  // Actions
  createOrder: (data: import('../../api/generated/trading/trading__api__trading/models').OrderCreateRequest) => Promise<void>;
  cancelOrder: (orderId: number) => Promise<void>;
  refreshPortfolio: () => Promise<void>;
  refreshOrders: () => Promise<void>;
}
