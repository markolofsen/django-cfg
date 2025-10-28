/**
 * WebSocket RPC Client - Public API
 *
 * Exports:
 * - React Context wrapper (WSRPCProvider, useWSRPC)
 * - Generated RPC client (RPCClient, ClientLogger, Types)
 * - Utilities (createRPCLogger, getSharedRPCLogger, token helpers)
 */

// React Context wrapper (recommended for React apps)
export { WSRPCProvider, useWSRPC } from './WSRPCContext';
export type { WSRPCContextValue, WSRPCProviderProps } from './WSRPCContext';

// Generated client (for advanced usage)
export { CentrifugoRPCClient, APIClient } from './generated';
export * as Types from './generated';

// Utilities
export {
  createRPCLogger,
  getSharedRPCLogger,
  resetSharedRPCLogger,
  // Token utilities
  decodeJWT,
  isTokenExpired,
  getTokenExpiry,
  getTimeUntilExpiry,
  maskToken,
  getTokenInfo,
} from './utils';
