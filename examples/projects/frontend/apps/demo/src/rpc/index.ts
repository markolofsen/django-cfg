/**
 * WebSocket RPC Client - Public API
 *
 * Exports:
 * - React Context wrapper (WSRPCProvider, useWSRPC)
 * - Generated RPC client (RPCClient, ClientLogger, Types)
 */

// React Context wrapper (recommended for React apps)
export { WSRPCProvider, useWSRPC } from './WSRPCContext';
export type { WSRPCContextValue, WSRPCProviderProps } from './WSRPCContext';

// Generated client (for advanced usage)
export { RPCClient, ClientLogger } from './generated';
export type { ClientLoggerConfig } from './generated';
export * as Types from './generated/types';
