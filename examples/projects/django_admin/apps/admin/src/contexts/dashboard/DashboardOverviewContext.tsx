/**
 * Dashboard Overview Context
 *
 * Manages complete dashboard overview data (all-in-one endpoint)
 *
 * Features:
 * - Complete dashboard data in single request
 * - Useful for initial page load
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiOverviewOverviewRetrieve,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_overview';

import type { DashboardOverview } from '@/api/generated/cfg/_utils/schemas/DashboardOverview.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardOverviewContextValue {
  // Complete overview
  overview?: DashboardOverview;
  isLoadingOverview: boolean;
  overviewError: Error | undefined;
  refreshOverview: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardOverviewContext = createContext<DashboardOverviewContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardOverviewProvider({ children }: { children: ReactNode }) {
  // Complete overview
  const {
    data: overview,
    error: overviewError,
    isLoading: isLoadingOverview,
    mutate: mutateOverview,
  } = useDashboardApiOverviewOverviewRetrieve(api);

  // Refresh function
  const refreshOverview = async () => {
    await mutateOverview();
  };

  const value: DashboardOverviewContextValue = {
    overview,
    isLoadingOverview,
    overviewError,
    refreshOverview,
  };

  return (
    <DashboardOverviewContext.Provider value={value}>
      {children}
    </DashboardOverviewContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardOverviewContext(): DashboardOverviewContextValue {
  const context = useContext(DashboardOverviewContext);
  if (!context) {
    throw new Error('useDashboardOverviewContext must be used within DashboardOverviewProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  DashboardOverview,
};
