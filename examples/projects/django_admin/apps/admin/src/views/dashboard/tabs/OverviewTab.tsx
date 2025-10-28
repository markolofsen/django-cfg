/**
 * OverviewTab Component
 *
 * Main overview tab showing key metrics and system status
 *
 * Features:
 * - Statistics cards
 * - System health radial chart
 * - Quick actions panel
 * - System metrics trend chart
 */

'use client';

import React from 'react';
import type { StatCard, SystemHealth, QuickAction, SystemMetrics } from '@/contexts/dashboard';

// Dashboard components
import { StatCardsGrid } from '../components/StatCardsGrid';
import { QuickActionsPanel } from '../components/QuickActionsPanel';

// Chart components
import { SystemHealthRadial } from '../components/SystemHealthRadial';
import { SystemMetricsChart } from '../components/SystemMetricsChart';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface OverviewTabProps {
  statCards?: StatCard | StatCard[];
  isLoadingStatCards?: boolean;
  systemHealth?: SystemHealth;
  isLoadingSystemHealth?: boolean;
  quickActions?: QuickAction[];
  isLoadingQuickActions?: boolean;
  systemMetrics?: SystemMetrics;
  isLoadingSystemMetrics?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function OverviewTab({
  statCards,
  isLoadingStatCards,
  systemHealth,
  isLoadingSystemHealth,
  quickActions,
  isLoadingQuickActions,
  systemMetrics,
  isLoadingSystemMetrics,
}: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Statistics Cards Grid */}
      <StatCardsGrid cards={statCards} isLoading={isLoadingStatCards} />

      {/* Charts Row - System Health & Metrics Trend */}
      <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
        {/* System Health Radial Chart */}
        <SystemHealthRadial
          health={systemHealth}
          isLoading={isLoadingSystemHealth}
        />

        {/* System Metrics Trend - spans 2 columns */}
        <div className="lg:col-span-2">
          <SystemMetricsChart
            metrics={systemMetrics}
            isLoading={isLoadingSystemMetrics}
          />
        </div>
      </div>

      {/* Quick Actions */}
      <QuickActionsPanel
        actions={quickActions}
        isLoading={isLoadingQuickActions}
      />
    </div>
  );
}
