/**
 * Centrifugo Monitoring Context
 *
 * Manages Centrifugo monitoring and metrics operations
 *
 * Features:
 * - Health checks
 * - Overview statistics
 * - Timeline statistics (time-series data)
 * - Recent publishes tracking with filtering
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useCentrifugoAdminApiMonitorHealthRetrieve,
  useCentrifugoAdminApiMonitorOverviewRetrieve,
  useCentrifugoAdminApiMonitorTimelineRetrieve,
  useCentrifugoAdminApiMonitorPublishesRetrieve,
} from '@/api/generated/cfg/_utils/hooks/cfg__centrifugo__centrifugo_monitoring';
import type { API } from '@/api/generated/cfg';
import type {
  HealthCheck,
  OverviewStats,
  ChannelList,
  RecentPublishes,
} from '@/api/generated/cfg/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface CentrifugoMonitoringContextValue {
  // Health
  health?: HealthCheck;
  isLoadingHealth: boolean;
  healthError: Error | undefined;
  refreshHealth: () => Promise<void>;

  // Overview stats
  overview?: OverviewStats;
  isLoadingOverview: boolean;
  overviewError: Error | undefined;
  refreshOverview: (hours?: number) => Promise<void>;

  // Timeline stats (time-series data)
  timeline?: ChannelList;
  isLoadingTimeline: boolean;
  timelineError: Error | undefined;
  refreshTimeline: (params?: { hours?: number; interval?: string }) => Promise<void>;

  // Recent publishes
  publishes?: RecentPublishes;
  isLoadingPublishes: boolean;
  publishesError: Error | undefined;
  refreshPublishes: (params?: { channel?: string; count?: number; offset?: number; status?: string }) => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const CentrifugoMonitoringContext = createContext<CentrifugoMonitoringContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function CentrifugoMonitoringProvider({ children }: { children: ReactNode }) {
  // Health check
  const {
    data: health,
    error: healthError,
    isLoading: isLoadingHealth,
    mutate: mutateHealth,
  } = useCentrifugoAdminApiMonitorHealthRetrieve(api as unknown as API);

  // Overview statistics
  const {
    data: overview,
    error: overviewError,
    isLoading: isLoadingOverview,
    mutate: mutateOverview,
  } = useCentrifugoAdminApiMonitorOverviewRetrieve(undefined, api as unknown as API);

  // Timeline statistics
  const {
    data: timeline,
    error: timelineError,
    isLoading: isLoadingTimeline,
    mutate: mutateTimeline,
  } = useCentrifugoAdminApiMonitorTimelineRetrieve(undefined, api as unknown as API);

  // Recent publishes
  const {
    data: publishes,
    error: publishesError,
    isLoading: isLoadingPublishes,
    mutate: mutatePublishes,
  } = useCentrifugoAdminApiMonitorPublishesRetrieve(undefined, api as unknown as API);

  // Refresh functions
  const refreshHealth = async () => {
    await mutateHealth();
  };

  const refreshOverview = async (hours?: number) => {
    await mutateOverview();
  };

  const refreshTimeline = async (params?: { hours?: number; interval?: string }) => {
    await mutateTimeline();
  };

  const refreshPublishes = async (params?: { channel?: string; count?: number; offset?: number; status?: string }) => {
    await mutatePublishes();
  };

  const value: CentrifugoMonitoringContextValue = {
    health,
    isLoadingHealth,
    healthError,
    refreshHealth,
    overview,
    isLoadingOverview,
    overviewError,
    refreshOverview,
    timeline,
    isLoadingTimeline,
    timelineError,
    refreshTimeline,
    publishes,
    isLoadingPublishes,
    publishesError,
    refreshPublishes,
  };

  return (
    <CentrifugoMonitoringContext.Provider value={value}>
      {children}
    </CentrifugoMonitoringContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useCentrifugoMonitoringContext(): CentrifugoMonitoringContextValue {
  const context = useContext(CentrifugoMonitoringContext);
  if (!context) {
    throw new Error('useCentrifugoMonitoringContext must be used within CentrifugoMonitoringProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  HealthCheck,
  OverviewStats,
  ChannelList,
  RecentPublishes,
};
