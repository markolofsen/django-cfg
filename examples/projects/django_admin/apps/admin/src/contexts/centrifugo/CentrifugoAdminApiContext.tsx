/**
 * Centrifugo Admin API Context
 *
 * Manages Centrifugo server administration operations
 *
 * Features:
 * - Server authentication tokens
 * - Channel listing and filtering
 * - Channel history retrieval
 * - Server info and stats
 * - Presence tracking
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useCreateCentrifugoAdminApiServerAuthTokenCreate,
  useCreateCentrifugoAdminApiServerChannelsCreate,
  useCreateCentrifugoAdminApiServerHistoryCreate,
  useCreateCentrifugoAdminApiServerInfoCreate,
  useCreateCentrifugoAdminApiServerPresenceCreate,
  useCreateCentrifugoAdminApiServerPresenceStatsCreate,
} from '@/api/generated/cfg/_utils/hooks/cfg__centrifugo__centrifugo_admin_api';
import type { API } from '@/api/generated/cfg';
import type {
  CentrifugoChannelsRequestRequest,
  CentrifugoChannelsResponse,
  CentrifugoHistoryRequestRequest,
  CentrifugoHistoryResponse,
  CentrifugoInfoResponse,
  CentrifugoPresenceRequestRequest,
  CentrifugoPresenceResponse,
  CentrifugoPresenceStatsRequestRequest,
  CentrifugoPresenceStatsResponse,
} from '@/api/generated/cfg/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface CentrifugoAdminApiContextValue {
  // Authentication
  getAuthToken: () => Promise<any>;

  // Channels
  listChannels: (data?: CentrifugoChannelsRequestRequest) => Promise<CentrifugoChannelsResponse>;
  getChannelHistory: (data: CentrifugoHistoryRequestRequest) => Promise<CentrifugoHistoryResponse>;

  // Server info
  getServerInfo: () => Promise<CentrifugoInfoResponse>;

  // Presence
  getPresence: (data: CentrifugoPresenceRequestRequest) => Promise<CentrifugoPresenceResponse>;
  getPresenceStats: (data: CentrifugoPresenceStatsRequestRequest) => Promise<CentrifugoPresenceStatsResponse>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const CentrifugoAdminApiContext = createContext<CentrifugoAdminApiContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function CentrifugoAdminApiProvider({ children }: { children: ReactNode }) {
  // Mutation hooks
  const getAuthTokenMutation = useCreateCentrifugoAdminApiServerAuthTokenCreate();
  const listChannelsMutation = useCreateCentrifugoAdminApiServerChannelsCreate();
  const getHistoryMutation = useCreateCentrifugoAdminApiServerHistoryCreate();
  const getInfoMutation = useCreateCentrifugoAdminApiServerInfoCreate();
  const getPresenceMutation = useCreateCentrifugoAdminApiServerPresenceCreate();
  const getPresenceStatsMutation = useCreateCentrifugoAdminApiServerPresenceStatsCreate();

  // Get authentication token for dashboard WebSocket connection
  const getAuthToken = async (): Promise<any> => {
    return await getAuthTokenMutation(api as unknown as API);
  };

  // List active channels with optional pattern filter
  const listChannels = async (data?: CentrifugoChannelsRequestRequest): Promise<CentrifugoChannelsResponse> => {
    return await listChannelsMutation(data || {}, api as unknown as API);
  };

  // Get channel message history
  const getChannelHistory = async (data: CentrifugoHistoryRequestRequest): Promise<CentrifugoHistoryResponse> => {
    return await getHistoryMutation(data, api as unknown as API);
  };

  // Get Centrifugo server information
  const getServerInfo = async (): Promise<CentrifugoInfoResponse> => {
    return await getInfoMutation(api as unknown as API);
  };

  // Get channel presence (list of subscribed clients)
  const getPresence = async (data: CentrifugoPresenceRequestRequest): Promise<CentrifugoPresenceResponse> => {
    return await getPresenceMutation(data, api as unknown as API);
  };

  // Get channel presence statistics
  const getPresenceStats = async (data: CentrifugoPresenceStatsRequestRequest): Promise<CentrifugoPresenceStatsResponse> => {
    return await getPresenceStatsMutation(data, api as unknown as API);
  };

  const value: CentrifugoAdminApiContextValue = {
    getAuthToken,
    listChannels,
    getChannelHistory,
    getServerInfo,
    getPresence,
    getPresenceStats,
  };

  return (
    <CentrifugoAdminApiContext.Provider value={value}>
      {children}
    </CentrifugoAdminApiContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useCentrifugoAdminApiContext(): CentrifugoAdminApiContextValue {
  const context = useContext(CentrifugoAdminApiContext);
  if (!context) {
    throw new Error('useCentrifugoAdminApiContext must be used within CentrifugoAdminApiProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  CentrifugoChannelsRequestRequest,
  CentrifugoChannelsResponse,
  CentrifugoHistoryRequestRequest,
  CentrifugoHistoryResponse,
  CentrifugoInfoResponse,
  CentrifugoPresenceRequestRequest,
  CentrifugoPresenceResponse,
  CentrifugoPresenceStatsRequestRequest,
  CentrifugoPresenceStatsResponse,
};
