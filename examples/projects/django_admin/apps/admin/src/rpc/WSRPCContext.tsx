/**
 * WebSocket RPC Context Provider
 *
 * Provides WebSocket RPC client to the entire app via React Context.
 * Wraps auto-generated RPC client with React state management.
 */

'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode, useMemo, useRef } from 'react';
import { APIClient, CentrifugoRPCClient } from './generated';
import { useAuth } from '@djangocfg/layouts';
import { settings } from '@/core/settings';
import { createRPCLogger, getTokenInfo, isTokenExpired } from './utils';

// ─────────────────────────────────────────────────────────────────────────
// Context Types
// ─────────────────────────────────────────────────────────────────────────

export interface WSRPCContextValue {
  // Connection State
  client: APIClient | null;
  baseClient: CentrifugoRPCClient | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  connectionState: string;

  // Connection Methods
  connect: () => Promise<void>;
  disconnect: () => void;
  reconnect: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const WSRPCContext = createContext<WSRPCContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider Props
// ─────────────────────────────────────────────────────────────────────────

export interface WSRPCProviderProps {
  children: ReactNode;
  /** Custom WebSocket URL (defaults to auto-detect from env) */
  url?: string;
  /** Auto-connect on mount (default: true) */
  autoConnect?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Provider Component
// ─────────────────────────────────────────────────────────────────────────

export function WSRPCProvider({
  children,
  url,
  autoConnect: autoConnectProp = true,
}: WSRPCProviderProps) {
  const { isAuthenticated, isLoading, getToken } = useAuth();

  const [client, setClient] = useState<APIClient | null>(null);
  const [baseClient, setBaseClient] = useState<CentrifugoRPCClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Create logger once with useMemo (cleaner than useRef + useEffect)
  const logger = useMemo(() => createRPCLogger(), []);

  // Reconnect timeout ref (needs useRef for mutable value)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Use custom URL or settings.api.wsUrl
  const wsUrl = url || settings.api.wsUrl;
  const autoConnect = autoConnectProp && (isAuthenticated && !isLoading);

  // Connection logic
  const connect = useCallback(async () => {
    if (isConnecting || isConnected) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      logger.info('Connecting to WebSocket RPC server...');

      // Get auth token
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      // Validate token before connecting
      const tokenInfo = getTokenInfo(token);
      logger.debug(`Token info: ${JSON.stringify({
        masked: tokenInfo.masked,
        expiresAt: tokenInfo.expiryFormatted,
        timeUntilExpiry: tokenInfo.timeUntilExpiryFormatted,
        isExpired: tokenInfo.isExpired,
      })}`);

      // Check if token is expired
      if (tokenInfo.isExpired) {
        throw new Error('Authentication token is expired. Please refresh the page to get a new token.');
      }

      // Warn if token expires soon (less than 5 minutes)
      if (tokenInfo.timeUntilExpiry !== null && tokenInfo.timeUntilExpiry < 5 * 60 * 1000) {
        logger.warning(`Token expires in ${tokenInfo.timeUntilExpiryFormatted}. Consider refreshing soon.`);
      }

      // Create client with token and user ID (extracted from token)
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      const userId = tokenPayload.user_id || tokenPayload.sub || '1';

      // Create base RPC client
      const baseRPC = new CentrifugoRPCClient(wsUrl, token, userId);
      await baseRPC.connect();

      // Create API client wrapper
      const rpcClient = new APIClient(baseRPC);

      setBaseClient(baseRPC);
      setClient(rpcClient);
      setIsConnected(true);
      setError(null);

      logger.success('WebSocket RPC connected successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Connection failed');
      setError(error);
      setBaseClient(null);
      setClient(null);
      setIsConnected(false);

      // Check if it's an authentication error
      const isAuthError = error.message.includes('token') ||
                          error.message.includes('auth') ||
                          error.message.includes('expired');

      if (isAuthError) {
        logger.error('WebSocket RPC authentication failed', error);
        logger.error('This usually means:');
        logger.error('1. The JWT token is expired - try refreshing the page');
        logger.error('2. The JWT secret key differs between frontend and backend');
        logger.error('3. The token format is incorrect');
        logger.error('Please check the server logs for more details.');
      } else {
        logger.error('WebSocket RPC connection failed', error);
      }

      // Only auto-reconnect for non-auth errors
      if (!isAuthError) {
        reconnectTimeoutRef.current = setTimeout(() => {
          logger.info('Attempting to reconnect...');
          connect();
        }, 5000);
      }
    } finally {
      setIsConnecting(false);
    }
  }, [wsUrl, isConnecting, isConnected, getToken, logger]);

  // Disconnect logic
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (baseClient) {
      logger.info('Disconnecting from WebSocket RPC server...');
      baseClient.disconnect();
      setBaseClient(null);
      setClient(null);
      setIsConnected(false);
      setError(null);
    }
  }, [baseClient, logger]);

  // Reconnect logic
  const reconnect = useCallback(async () => {
    disconnect();
    await connect();
  }, [connect, disconnect]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]); // Only run on mount/unmount

  // Connection state string for UI display
  const connectionState = isConnected
    ? 'connected'
    : isConnecting
    ? 'connecting'
    : error
    ? 'error'
    : 'disconnected';

  const value: WSRPCContextValue = {
    client,
    baseClient,
    isConnected,
    isConnecting,
    error,
    connectionState,
    connect,
    disconnect,
    reconnect,
  };

  return (
    <WSRPCContext.Provider value={value}>
      {children}
    </WSRPCContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook to use WebSocket RPC Context
// ─────────────────────────────────────────────────────────────────────────

export function useWSRPC(): WSRPCContextValue {
  const context = useContext(WSRPCContext);

  if (context === undefined) {
    throw new Error('useWSRPC must be used within a WSRPCProvider');
  }

  return context;
}
