/**
 * WebSocket RPC Client - Public API
 *
 * Exports:
 * - React Context wrapper (WSRPCProvider, useWSRPC)
 * - Generated RPC client (RPCClient, ClientLogger, Types)
 * - Utilities (useRPCLogger hook)
 */

// React Context wrapper (recommended for React apps)
export { WSRPCProvider, useWSRPC } from './utils/context';
export type { WSRPCContextValue, WSRPCProviderProps } from './utils/context';

// RPC Logger hook
export { useRPCLogger } from './utils/useLogger';
export type { RPCLogger } from './utils/useLogger';

// Generated client (for advanced usage)
export { CentrifugoRPCClient, APIClient } from './generated';
export * as Types from './generated';

// Hooks for channel subscriptions
export { useSubscription } from './utils/useSubscription';
export type { useSubscriptionOptions } from './utils/useSubscription';