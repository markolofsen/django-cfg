/**
 * Dashboard Activity Context
 *
 * Manages activity tracking and quick actions
 *
 * Features:
 * - Recent activity entries
 * - Quick action buttons
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiActivityRecentList,
  useDashboardApiActivityActionsList,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_activity';

import type { ActivityEntry } from '@/api/generated/cfg/_utils/schemas/ActivityEntry.schema';
import type { QuickAction } from '@/api/generated/cfg/_utils/schemas/QuickAction.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardActivityContextValue {
  // Recent activity
  recentActivity?: ActivityEntry[];
  isLoadingRecentActivity: boolean;
  recentActivityError: Error | undefined;
  refreshRecentActivity: () => Promise<void>;

  // Quick actions
  quickActions?: QuickAction[];
  isLoadingQuickActions: boolean;
  quickActionsError: Error | undefined;
  refreshQuickActions: () => Promise<void>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardActivityContext = createContext<DashboardActivityContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardActivityProvider({ children }: { children: ReactNode }) {
  // Recent activity
  const {
    data: recentActivity,
    error: recentActivityError,
    isLoading: isLoadingRecentActivity,
    mutate: mutateRecentActivity,
  } = useDashboardApiActivityRecentList(undefined, api);

  // Quick actions
  const {
    data: quickActions,
    error: quickActionsError,
    isLoading: isLoadingQuickActions,
    mutate: mutateQuickActions,
  } = useDashboardApiActivityActionsList(api);

  // Refresh functions
  const refreshRecentActivity = async () => {
    await mutateRecentActivity();
  };

  const refreshQuickActions = async () => {
    await mutateQuickActions();
  };

  const refreshAll = async () => {
    await Promise.all([mutateRecentActivity(), mutateQuickActions()]);
  };

  const value: DashboardActivityContextValue = {
    recentActivity,
    isLoadingRecentActivity,
    recentActivityError,
    refreshRecentActivity,

    quickActions,
    isLoadingQuickActions,
    quickActionsError,
    refreshQuickActions,

    refreshAll,
  };

  return (
    <DashboardActivityContext.Provider value={value}>
      {children}
    </DashboardActivityContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardActivityContext(): DashboardActivityContextValue {
  const context = useContext(DashboardActivityContext);
  if (!context) {
    throw new Error('useDashboardActivityContext must be used within DashboardActivityProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  ActivityEntry,
  QuickAction,
};
