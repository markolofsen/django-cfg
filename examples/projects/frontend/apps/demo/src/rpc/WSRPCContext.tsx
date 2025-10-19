/**
 * WebSocket RPC Context Provider
 *
 * Provides WebSocket RPC client to the entire app via React Context.
 * Wraps auto-generated RPC client with React state management.
 */

'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode, useRef } from 'react';
import { RPCClient, ClientLogger } from './generated';
import { useAuth } from '@djangocfg/layouts';
import { isDevelopment } from '@/core/settings';

// ─────────────────────────────────────────────────────────────────────────
// Context Types
// ─────────────────────────────────────────────────────────────────────────

export interface WSRPCContextValue {
  // Connection State
  client: RPCClient | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  connectionState: string;

  // Connection Methods
  connect: () => Promise<void>;
  disconnect: () => void;
  reconnect: () => Promise<void>;

  // RPC Methods (typed from generated client)
  workspace: {
    list: (params: any) => Promise<any>;
    fileChanged: (params: any) => Promise<any>;
    snapshotCreated: (params: any) => Promise<any>;
    stateChanged: (params: any) => Promise<any>;
  };
  session: {
    message: (params: any) => Promise<any>;
    taskStatus: (params: any) => Promise<any>;
    contextUpdated: (params: any) => Promise<any>;
  };
  notification: {
    send: (params: any) => Promise<any>;
    broadcast: (params: any) => Promise<any>;
  };
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
  const { isAuthenticated, isLoading } = useAuth();

  const [client, setClient] = useState<RPCClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loggerRef = useRef<ClientLogger | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Use custom URL or environment variable or auto-detect
  const wsUrl = url || process.env.NEXT_PUBLIC_WS_RPC_URL;
  const autoConnect = autoConnectProp && (isAuthenticated && !isLoading);

  // Initialize logger
  useEffect(() => {
    if (!loggerRef.current) {
      loggerRef.current = new ClientLogger({
        level: isDevelopment ? 4 : 3, // DEBUG : INFO
        logRPCCalls: isDevelopment,
      });
    }
  }, [isDevelopment]);

  // Connection logic
  const connect = useCallback(async () => {
    if (isConnecting || isConnected) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      loggerRef.current?.info('Connecting to WebSocket RPC server...');

      const rpcClient = wsUrl ? new RPCClient(wsUrl) : RPCClient.fromEnv();
      await rpcClient.connect();

      setClient(rpcClient);
      setIsConnected(true);
      setError(null);

      loggerRef.current?.success('WebSocket RPC connected successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Connection failed');
      setError(error);
      setClient(null);
      setIsConnected(false);

      loggerRef.current?.error('WebSocket RPC connection failed', error);

      // Auto-reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        loggerRef.current?.info('Attempting to reconnect...');
        connect();
      }, 5000);
    } finally {
      setIsConnecting(false);
    }
  }, [wsUrl, isConnecting, isConnected]);

  // Disconnect logic
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (client) {
      loggerRef.current?.info('Disconnecting from WebSocket RPC server...');
      client.disconnect();
      setClient(null);
      setIsConnected(false);
      setError(null);
    }
  }, [client]);

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

  // ─────────────────────────────────────────────────────────────────────────
  // RPC Method Wrappers
  // ─────────────────────────────────────────────────────────────────────────

  const workspace = {
    list: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      // Use generic call method for workspace.list
      return (client as any).call('workspace.list', params);
    }, [client]),

    fileChanged: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.workspaceFileChanged(params);
    }, [client]),

    snapshotCreated: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.workspaceSnapshotCreated(params);
    }, [client]),

    stateChanged: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.workspaceStateChanged(params);
    }, [client]),
  };

  const session = {
    message: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.sessionMessage(params);
    }, [client]),

    taskStatus: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.sessionTaskStatus(params);
    }, [client]),

    contextUpdated: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.sessionContextUpdated(params);
    }, [client]),
  };

  const notification = {
    send: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.notificationSend(params);
    }, [client]),

    broadcast: useCallback(async (params: any) => {
      if (!client) throw new Error('RPC client not connected');
      return client.notificationBroadcast(params);
    }, [client]),
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Context Value
  // ─────────────────────────────────────────────────────────────────────────

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
    isConnected,
    isConnecting,
    error,
    connectionState,
    connect,
    disconnect,
    reconnect,
    workspace,
    session,
    notification,
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
