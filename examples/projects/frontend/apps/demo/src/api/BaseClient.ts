/**
 * BaseClient for Demo App API Services
 *
 * Base class for all demo app services.
 *
 * Architecture:
 * - Profiles Group: User profiles management
 * - Trading Group: Portfolio and orders management
 * - Crypto Group: Coins, exchanges, and wallets
 *
 * Uses unified response pattern: { success, boolean; data?: T; error?: string; fieldErrors?: Record<string, string[]> }
 */

import { API as ProfilesAPI, LocalStorageAdapter as ProfilesStorage } from './generated/profiles';
import { API as TradingAPI, LocalStorageAdapter as TradingStorage } from './generated/trading';
import { API as CryptoAPI, LocalStorageAdapter as CryptoStorage } from './generated/crypto';
import { APIError } from './generated/profiles/errors';

// Get base URL from environment
const baseUrl = typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL
  : 'http://localhost:8000';

// API endpoints for each group
const profilesUrl = `${baseUrl}/api/profiles`;
const tradingUrl = `${baseUrl}/api/trading`;
const cryptoUrl = `${baseUrl}/api/crypto`;

// Create singleton API instances for each group
const profilesApi = new ProfilesAPI(profilesUrl, { storage: new ProfilesStorage() });
const tradingApi = new TradingAPI(tradingUrl, { storage: new TradingStorage() });
const cryptoApi = new CryptoAPI(cryptoUrl, { storage: new CryptoStorage() });

export class BaseClient {
  /**
   * Profiles API client
   * Available: this.profilesApi.profiles__api__profiles
   */
  protected static profilesApi = profilesApi;

  /**
   * Trading API client
   * Available:
   * - this.tradingApi.trading_trading.portfolios
   * - this.tradingApi.trading_trading.orders
   */
  protected static tradingApi = tradingApi;

  /**
   * Crypto API client
   * Available:
   * - this.cryptoApi.crypto_crypto.coins
   * - this.cryptoApi.crypto_crypto.exchanges
   * - this.cryptoApi.crypto_crypto.wallets
   */
  protected static cryptoApi = cryptoApi;
}

// Export API instances and error classes
export { profilesApi, tradingApi as tradingClient, cryptoApi as cryptoClient, APIError };
