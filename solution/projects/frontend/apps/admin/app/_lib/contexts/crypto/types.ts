/**
 * Crypto Context Types
 * Single source of truth for crypto-related types
 */

import type { CoinList, CoinStats, Exchange, Wallet } from '../../api/generated/_crypto';

// Re-export schema types from generated API
export type { CoinList, CoinStats, Exchange, Wallet };

// Context state types
export interface CryptoContextType {
  // Coins data
  coins: CoinList[];
  coinsLoading: boolean;
  coinsError: Error | null;
  coinStats: CoinStats | undefined;

  // Exchanges data
  exchanges: Exchange[];
  exchangesLoading: boolean;
  exchangesError: Error | null;

  // Wallets data
  wallets: Wallet[];
  walletsLoading: boolean;
  walletsError: Error | null;

  // Actions
  refreshCoins: () => Promise<void>;
  refreshExchanges: () => Promise<void>;
  refreshWallets: () => Promise<void>;
}
