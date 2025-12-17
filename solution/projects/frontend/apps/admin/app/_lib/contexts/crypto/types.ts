/**
 * Crypto Context Types
 * Single source of truth for crypto-related types
 */

// Re-export schema types from generated API
export type { CoinList } from '../../api/generated/crypto/_utils/schemas/CoinList.schema';
export type { CoinStats } from '../../api/generated/crypto/_utils/schemas/CoinStats.schema';
export type { Exchange } from '../../api/generated/crypto/_utils/schemas/Exchange.schema';
export type { Wallet } from '../../api/generated/crypto/_utils/schemas/Wallet.schema';

// Context state types
export interface CryptoContextType {
  // Coins data
  coins: import('../../api/generated/crypto/_utils/schemas/CoinList.schema').CoinList[];
  coinsLoading: boolean;
  coinsError: Error | null;
  coinStats: import('../../api/generated/crypto/_utils/schemas/CoinStats.schema').CoinStats | undefined;

  // Exchanges data
  exchanges: import('../../api/generated/crypto/_utils/schemas/Exchange.schema').Exchange[];
  exchangesLoading: boolean;
  exchangesError: Error | null;

  // Wallets data
  wallets: import('../../api/generated/crypto/_utils/schemas/Wallet.schema').Wallet[];
  walletsLoading: boolean;
  walletsError: Error | null;

  // Actions
  refreshCoins: () => Promise<void>;
  refreshExchanges: () => Promise<void>;
  refreshWallets: () => Promise<void>;
}
