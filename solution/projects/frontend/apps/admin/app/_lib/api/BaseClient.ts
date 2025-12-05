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
import { API as TerminalAPI, LocalStorageAdapter as TerminalStorage } from './generated/terminal';
import { APIError } from './generated/profiles/errors';
import { settings } from '@core/settings';
import consola from 'consola';

// Get base URL from environment
const baseUrl = settings.api.baseUrl;

consola.log('[BaseClient] baseUrl', baseUrl);

// Create singleton API instances for each group
// NOTE: The generated clients already include the full path (e.g., /api/trading/orders/)
// so we only pass the base URL without any prefixes
const profilesApi = new ProfilesAPI(baseUrl, { storage: new ProfilesStorage() });
const tradingApi = new TradingAPI(baseUrl, { storage: new TradingStorage() });
const cryptoApi = new CryptoAPI(baseUrl, { storage: new CryptoStorage() });
const terminalApi = new TerminalAPI(baseUrl, { storage: new TerminalStorage() });

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

  /**
   * Terminal API client
   * Available:
   * - this.terminalApi.terminal_terminal.sessions
   * - this.terminalApi.terminal_terminal.commands
   */
  protected static terminalApi = terminalApi;
}

// Export API instances and error classes
export { profilesApi, tradingApi as tradingClient, cryptoApi as cryptoClient, terminalApi as terminalClient, APIError };
