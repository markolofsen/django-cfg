import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedOrderList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<Order>;
}

/**
 * Serializer for creating orders.
 * 
 * Request model (no read-only fields).
 */
export interface OrderCreateRequest {
  /** Trading pair (e.g., BTC/USDT) */
  symbol: string;
  /** * `market` - Market
  * `limit` - Limit
  * `stop_loss` - Stop Loss */
  order_type?: Enums.OrderCreateRequestOrderType;
  /** * `buy` - Buy
  * `sell` - Sell */
  side: Enums.OrderCreateRequestSide;
  quantity: string;
  price?: string | null;
}

/**
 * Serializer for creating orders.
 * 
 * Response model (includes read-only fields).
 */
export interface OrderCreate {
  /** Trading pair (e.g., BTC/USDT) */
  symbol: string;
  /** * `market` - Market
  * `limit` - Limit
  * `stop_loss` - Stop Loss */
  order_type?: Enums.OrderCreateOrderType;
  /** * `buy` - Buy
  * `sell` - Sell */
  side: Enums.OrderCreateSide;
  quantity: string;
  price?: string | null;
}

/**
 * Serializer for orders.
 * 
 * Response model (includes read-only fields).
 */
export interface Order {
  id: number;
  portfolio: number;
  /** Trading pair (e.g., BTC/USDT) */
  symbol: string;
  /** * `market` - Market
  * `limit` - Limit
  * `stop_loss` - Stop Loss */
  order_type?: Enums.OrderOrderType;
  /** * `buy` - Buy
  * `sell` - Sell */
  side: Enums.OrderSide;
  quantity: string;
  price?: string | null;
  filled_quantity: string;
  /** * `pending` - Pending
  * `filled` - Filled
  * `cancelled` - Cancelled */
  status: Enums.OrderStatus;
  total_usd: string;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for orders.
 * 
 * Request model (no read-only fields).
 */
export interface OrderRequest {
  portfolio: number;
  /** Trading pair (e.g., BTC/USDT) */
  symbol: string;
  /** * `market` - Market
  * `limit` - Limit
  * `stop_loss` - Stop Loss */
  order_type?: Enums.OrderRequestOrderType;
  /** * `buy` - Buy
  * `sell` - Sell */
  side: Enums.OrderRequestSide;
  quantity: string;
  price?: string | null;
}

/**
 * Serializer for orders.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedOrderRequest {
  portfolio?: number;
  /** Trading pair (e.g., BTC/USDT) */
  symbol?: string;
  /** * `market` - Market
  * `limit` - Limit
  * `stop_loss` - Stop Loss */
  order_type?: Enums.PatchedOrderRequestOrderType;
  /** * `buy` - Buy
  * `sell` - Sell */
  side?: Enums.PatchedOrderRequestSide;
  quantity?: string;
  price?: string | null;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPortfolioList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<Portfolio>;
}

/**
 * Serializer for trading portfolios.
 * 
 * Response model (includes read-only fields).
 */
export interface Portfolio {
  id: number;
  user: number;
  user_info: Record<string, any>;
  /** Total portfolio value in USD */
  total_balance_usd: string;
  /** Available balance for trading */
  available_balance_usd?: string;
  total_profit_loss: string;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for portfolio statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface PortfolioStats {
  total_portfolios: number;
  total_volume_usd: string;
  total_orders: number;
}

