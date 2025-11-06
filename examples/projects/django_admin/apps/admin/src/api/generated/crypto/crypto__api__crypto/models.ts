/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedCoinListList {
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
  results: Array<CoinList>;
}

/**
 * Serializer for coins.
 * 
 * Response model (includes read-only fields).
 */
export interface Coin {
  id: number;
  /** Coin symbol (e.g., BTC, ETH) */
  symbol: string;
  /** Full name (e.g., Bitcoin, Ethereum) */
  name: string;
  slug: string;
  /** Current price in USD */
  current_price_usd?: string;
  /** Market capitalization */
  market_cap_usd?: string;
  /** 24h trading volume */
  volume_24h_usd?: string;
  price_change_24h_percent?: string;
  price_change_7d_percent?: string;
  price_change_30d_percent?: string;
  logo_url?: string;
  description?: string;
  website?: string;
  whitepaper_url?: string;
  /** Market cap rank */
  rank?: number;
  is_active?: boolean;
  is_tradeable?: boolean;
  is_price_up_24h: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for coin statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface CoinStats {
  total_coins: number;
  total_market_cap_usd: string;
  total_volume_24h_usd: string;
  trending_coins: Array<CoinList>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedExchangeList {
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
  results: Array<Exchange>;
}

/**
 * Serializer for exchanges.
 * 
 * Response model (includes read-only fields).
 */
export interface Exchange {
  id: number;
  /** Exchange name */
  name: string;
  slug: string;
  /** Exchange code (e.g., BINANCE, COINBASE) */
  code: string;
  description?: string;
  website?: string;
  logo_url?: string;
  /** 24h trading volume */
  volume_24h_usd?: string;
  /** Number of trading pairs */
  num_markets?: number;
  /** Number of supported coins */
  num_coins?: number;
  maker_fee_percent?: string;
  taker_fee_percent?: string;
  is_active?: boolean;
  is_verified?: boolean;
  supports_api?: boolean;
  /** Exchange rank by volume */
  rank?: number;
  created_at: string;
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedWalletList {
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
  results: Array<Wallet>;
}

/**
 * Serializer for wallets.
 * 
 * Response model (includes read-only fields).
 */
export interface Wallet {
  id: number;
  user: number;
  coin: number;
  coin_info: CoinList;
  /** Available balance */
  balance?: string;
  /** Locked balance (in orders) */
  locked_balance: string;
  total_balance: string;
  value_usd: string;
  /** Deposit address */
  address?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Lightweight serializer for coin lists.
 * 
 * Response model (includes read-only fields).
 */
export interface CoinList {
  id: number;
  /** Coin symbol (e.g., BTC, ETH) */
  symbol: string;
  /** Full name (e.g., Bitcoin, Ethereum) */
  name: string;
  slug: string;
  /** Current price in USD */
  current_price_usd?: string;
  /** Market capitalization */
  market_cap_usd?: string;
  price_change_24h_percent?: string;
  logo_url?: string;
  /** Market cap rank */
  rank?: number;
  is_price_up_24h: boolean;
}

