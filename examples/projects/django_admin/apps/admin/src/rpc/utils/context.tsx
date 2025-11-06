/**
 * WebSocket RPC Context Provider
 *
 * Provides WebSocket RPC client to the entire app via React Context.
 * Wraps auto-generated RPC client with React state management.
 */

'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode, useRef, useMemo } from 'react';
import { APIClient, CentrifugoRPCClient } from '../generated';
import { useAuth } from '@djangocfg/layouts';
import { useRPCLogger } from './useLogger';
import { useDashboardOverviewContext } from '@/contexts/dashboard';

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
  const { isAuthenticated, isLoading, user } = useAuth();
  const { djangoConfig } = useDashboardOverviewContext();

  const [client, setClient] = useState<APIClient | null>(null);
  const [baseClient, setBaseClient] = useState<CentrifugoRPCClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Use RPC logger hook
  const logger = useRPCLogger();

  // Reconnect timeout ref (needs useRef for mutable value)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Track if we've ever successfully connected (prevents double-connect in Strict Mode)
  const hasConnectedRef = useRef(false);

  // Track if connection is in progress (prevents cleanup from disconnecting during async connect)
  const isConnectingRef = useRef(false);

  // Track if component is mounted (prevents state updates after unmount)
  const isMountedRef = useRef(true);

  // Get Centrifugo data from user profile (must be before wsUrl)
  const centrifugoToken = user?.centrifugo;
  const centrifugoEnabled = djangoConfig?.centrifugo?.enabled ?? false;
  const hasCentrifugoToken = !!centrifugoToken?.token;

  // Use custom URL, centrifugo_url from profile, settings.api.wsUrl, or auto-detect from hostname
  const wsUrl = useMemo(() => {
    if (url) {
      // 1. Explicit URL prop (highest priority)
      return url;
    }
    if (centrifugoToken?.centrifugo_url) {
      // 2. URL from user profile (dynamic from backend)
      return centrifugoToken.centrifugo_url;
    }
  }, [url, centrifugoToken?.centrifugo_url]);

  // Only auto-connect if:
  // 1. User is authenticated and not loading
  // 2. Centrifugo is enabled in Django config
  // 3. Centrifugo token is available in user profile
  const autoConnect = autoConnectProp &&
                      (isAuthenticated && !isLoading) &&
                      centrifugoEnabled &&
                      hasCentrifugoToken;

  // Log connection decision
  useEffect(() => {
    if (!isLoading && djangoConfig) {
      logger.info(`[RPC] Auto-connect decision: ${autoConnect ? 'YES' : 'NO'}`);
      logger.info(`[RPC]   - Authenticated: ${isAuthenticated}`);
      logger.info(`[RPC]   - Auth loading: ${isLoading}`);
      logger.info(`[RPC]   - Centrifugo enabled: ${centrifugoEnabled}`);
      logger.info(`[RPC]   - Centrifugo token from profile: ${hasCentrifugoToken}`);
      logger.info(`[RPC]   - WebSocket URL: ${wsUrl}`);

      if (centrifugoToken?.centrifugo_url) {
        logger.info(`[RPC]   - URL source: user profile (${centrifugoToken.centrifugo_url})`);
      } else {
        logger.info(`[RPC]   - URL source: auto-detected`);
      }

      if (hasCentrifugoToken && centrifugoToken) {
        logger.info(`[RPC]   - Channels: ${centrifugoToken.channels?.join(', ')}`);
      }
    }
  }, [autoConnect, isAuthenticated, isLoading, centrifugoEnabled, hasCentrifugoToken, centrifugoToken, djangoConfig, logger, wsUrl]);

  // Connection logic
  const connect = useCallback(async () => {
    // Check ref first to prevent Strict Mode double-connect
    if (hasConnectedRef.current || isConnectingRef.current) {
      return;
    }

    if (isConnecting || isConnected) {
      return;
    }

    isConnectingRef.current = true; // Mark connecting immediately
    setIsConnecting(true);
    setError(null);

    try {
      logger.info('Connecting to WebSocket RPC server...');

      // Get Centrifugo token from user profile
      if (!centrifugoToken?.token) {
        throw new Error('No Centrifugo token available in user profile. Please refresh the page.');
      }

      const token = centrifugoToken.token;
      const channels = centrifugoToken.channels;

      logger.debug(`Centrifugo token from profile with ${channels?.length || 0} channels: ${channels?.join(', ')}`);


      // Get user ID from auth context (fallback to parsing token)
      let userId = user?.id?.toString() || '1';

      // If no user from context, try to extract from token
      if (!user?.id) {
        try {
          const tokenPayload = JSON.parse(atob(token.split('.')[1]));
          userId = tokenPayload.user_id?.toString() || tokenPayload.sub?.toString() || '1';
        } catch (err) {
          // Silently fallback to default userId
        }
      }

      // Create base RPC client
      const baseRPC = new CentrifugoRPCClient(wsUrl, token, userId);

      await baseRPC.connect();

      // Check if component was unmounted while we were connecting
      if (!isMountedRef.current) {
        baseRPC.disconnect();
        isConnectingRef.current = false;
        return;
      }

      // Create API client wrapper
      const rpcClient = new APIClient(baseRPC);

      // Mark as connected BEFORE setting state (prevents cleanup from disconnecting)
      hasConnectedRef.current = true;
      isConnectingRef.current = false;

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
      hasConnectedRef.current = false; // Reset ref on error
      isConnectingRef.current = false; // Reset connecting ref on error

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
  }, [wsUrl, centrifugoToken, user, logger]); // Use centrifugoToken from user profile

  // Disconnect logic
  const disconnect = useCallback(() => {
    // Don't disconnect if connection is in progress (prevents Strict Mode cleanup from interrupting)
    if (isConnectingRef.current) {
      return;
    }

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

    // Reset ref to allow future connections
    hasConnectedRef.current = false;
    isConnectingRef.current = false;
  }, [baseClient, logger]);

  // Reconnect logic
  const reconnect = useCallback(async () => {
    disconnect();
    await connect();
  }, [connect, disconnect]);

  // Auto-connect on mount
  useEffect(() => {
    // Mark as mounted
    isMountedRef.current = true;

    if (autoConnect && !hasConnectedRef.current) {
      connect();
    }

    return () => {
      // Only disconnect if we're connecting (React Strict Mode double-mount)
      // If we're already connected (hasConnectedRef = true), keep the connection
      if (isConnectingRef.current && !hasConnectedRef.current) {
        return;
      }

      // Real unmount or effect re-run after successful connection
      // Only disconnect in these cases
      if (!hasConnectedRef.current) {
        return;
      }

      isMountedRef.current = false;
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]); // Only depend on autoConnect - connect/disconnect are stable refs

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
