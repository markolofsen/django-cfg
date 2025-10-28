/**
 * Dashboard System Context
 *
 * Manages system health and metrics data
 *
 * Features:
 * - System health status
 * - System performance metrics
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiSystemHealthRetrieve,
  useDashboardApiSystemMetricsRetrieve,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_system';

import type { SystemHealth } from '@/api/generated/cfg/_utils/schemas/SystemHealth.schema';
import type { SystemMetrics } from '@/api/generated/cfg/_utils/schemas/SystemMetrics.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardSystemContextValue {
  // System health
  health?: SystemHealth;
  isLoadingHealth: boolean;
  healthError: Error | undefined;
  refreshHealth: () => Promise<void>;

  // System metrics
  metrics?: SystemMetrics;
  isLoadingMetrics: boolean;
  metricsError: Error | undefined;
  refreshMetrics: () => Promise<void>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardSystemContext = createContext<DashboardSystemContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardSystemProvider({ children }: { children: ReactNode }) {
  // System health
  const {
    data: health,
    error: healthError,
    isLoading: isLoadingHealth,
    mutate: mutateHealth,
  } = useDashboardApiSystemHealthRetrieve(api);

  // System metrics
  const {
    data: metrics,
    error: metricsError,
    isLoading: isLoadingMetrics,
    mutate: mutateMetrics,
  } = useDashboardApiSystemMetricsRetrieve(api);

  // Refresh functions
  const refreshHealth = async () => {
    await mutateHealth();
  };

  const refreshMetrics = async () => {
    await mutateMetrics();
  };

  const refreshAll = async () => {
    await Promise.all([mutateHealth(), mutateMetrics()]);
  };

  const value: DashboardSystemContextValue = {
    health,
    isLoadingHealth,
    healthError,
    refreshHealth,

    metrics,
    isLoadingMetrics,
    metricsError,
    refreshMetrics,

    refreshAll,
  };

  return (
    <DashboardSystemContext.Provider value={value}>
      {children}
    </DashboardSystemContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardSystemContext(): DashboardSystemContextValue {
  const context = useContext(DashboardSystemContext);
  if (!context) {
    throw new Error('useDashboardSystemContext must be used within DashboardSystemProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  SystemHealth,
  SystemMetrics,
};
