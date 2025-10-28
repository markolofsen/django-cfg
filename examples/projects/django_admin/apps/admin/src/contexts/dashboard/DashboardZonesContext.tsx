/**
 * Dashboard API Zones Context
 *
 * Manages OpenAPI zones/groups data
 *
 * Features:
 * - List all API zones with configuration
 * - Zones summary with statistics
 * - Zone details (apps, endpoints, status)
 * - Pagination support
 *
 * Usage:
 * ```tsx
 * import { DashboardZonesProvider, useDashboardZonesContext } from '@/contexts/dashboard';
 *
 * function App() {
 *   return (
 *     <DashboardZonesProvider>
 *       <ZonesView />
 *     </DashboardZonesProvider>
 *   );
 * }
 *
 * function ZonesView() {
 *   const { zones, summary, isLoadingZones } = useDashboardZonesContext();
 *
 *   return (
 *     <div>
 *       <ZonesSummary data={summary} />
 *       <ZonesList zones={zones?.results} />
 *     </div>
 *   );
 * }
 * ```
 */

'use client';

import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiZonesList,
  useDashboardApiZonesSummaryRetrieve,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_api_zones';

import type { APIZonesSummary } from '@/api/generated/cfg/_utils/schemas/APIZonesSummary.schema';
import type { APIZone } from '@/api/generated/cfg/_utils/schemas/APIZone.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardZonesContextValue {
  // API Zones list (simple array, no pagination)
  zones?: APIZone[];
  isLoadingZones: boolean;
  zonesError: Error | undefined;
  refreshZones: () => Promise<void>;

  // Zones summary
  summary?: APIZonesSummary;
  isLoadingSummary: boolean;
  summaryError: Error | undefined;
  refreshSummary: () => Promise<void>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardZonesContext = createContext<DashboardZonesContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardZonesProvider({ children }: { children: ReactNode }) {
  // API Zones list (returns array directly, no pagination)
  const {
    data: zones,
    error: zonesError,
    isLoading: isLoadingZones,
    mutate: mutateZones,
  } = useDashboardApiZonesList(api);

  // Zones summary
  const {
    data: summary,
    error: summaryError,
    isLoading: isLoadingSummary,
    mutate: mutateSummary,
  } = useDashboardApiZonesSummaryRetrieve(api);

  // Refresh functions
  const refreshZones = async () => {
    await mutateZones();
  };

  const refreshSummary = async () => {
    await mutateSummary();
  };

  const refreshAll = async () => {
    await Promise.all([mutateZones(), mutateSummary()]);
  };

  const value: DashboardZonesContextValue = {
    zones,
    isLoadingZones,
    zonesError,
    refreshZones,

    summary,
    isLoadingSummary,
    summaryError,
    refreshSummary,

    refreshAll,
  };

  return (
    <DashboardZonesContext.Provider value={value}>
      {children}
    </DashboardZonesContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardZonesContext(): DashboardZonesContextValue {
  const context = useContext(DashboardZonesContext);
  if (!context) {
    throw new Error('useDashboardZonesContext must be used within DashboardZonesProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  APIZonesSummary,
  APIZone,
};
