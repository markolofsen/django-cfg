/**
 * Centrifugo View Types
 *
 * Re-exports types from Centrifugo contexts
 */

export type {
  // Monitoring types
  HealthCheck,
  OverviewStats,
  ChannelList,
  RecentPublishes,
  // Admin API types
  CentrifugoChannelsRequestRequest,
  CentrifugoChannelsResponse,
  CentrifugoHistoryRequestRequest,
  CentrifugoHistoryResponse,
  CentrifugoInfoResponse,
  CentrifugoPresenceRequestRequest,
  CentrifugoPresenceResponse,
  CentrifugoPresenceStatsRequestRequest,
  CentrifugoPresenceStatsResponse,
  // Testing types
  ConnectionTokenRequestRequest,
  ConnectionTokenResponse,
  PublishTestRequestRequest,
  PublishTestResponse,
  ManualAckRequestRequest,
  ManualAckResponse,
} from '@/contexts/centrifugo';

// Tab types
export type TabType = 'overview' | 'publishes' | 'channels' | 'live-channels' | 'testing';
