/**
 * SystemTab Component
 *
 * Detailed system health and metrics tab
 *
 * Features:
 * - System health components list
 * - System metrics chart
 * - System metrics panel with details
 * - Recent system activity
 */

'use client';

import React from 'react';
import type { SystemHealth, SystemMetrics, ActivityEntry } from '@/contexts/dashboard';

// Dashboard components
import { SystemHealthWidget } from '../components/SystemHealthWidget';
import { SystemMetricsPanel } from '../components/SystemMetricsPanel';
import { RecentActivityList } from '../components/RecentActivityList';

// Chart components
import { SystemMetricsChart } from '../components/SystemMetricsChart';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface SystemTabProps {
  systemHealth?: SystemHealth;
  isLoadingSystemHealth?: boolean;
  systemMetrics?: SystemMetrics;
  isLoadingSystemMetrics?: boolean;
  recentActivity?: ActivityEntry[];
  isLoadingRecentActivity?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function SystemTab({
  systemHealth,
  isLoadingSystemHealth,
  systemMetrics,
  isLoadingSystemMetrics,
  recentActivity,
  isLoadingRecentActivity,
}: SystemTabProps) {
  return (
    <div className="space-y-6">
      {/* System Metrics Trend Chart - Full Width */}
      <SystemMetricsChart
        metrics={systemMetrics}
        isLoading={isLoadingSystemMetrics}
      />

      {/* Main Grid */}
      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          {/* System Health Components List */}
          <SystemHealthWidget
            health={systemHealth}
            isLoading={isLoadingSystemHealth}
          />

          {/* System Metrics Panel */}
          <SystemMetricsPanel
            metrics={systemMetrics}
            isLoading={isLoadingSystemMetrics}
          />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Recent System Activity */}
          <RecentActivityList
            activities={recentActivity}
            isLoading={isLoadingRecentActivity}
            maxItems={20}
          />
        </div>
      </div>
    </div>
  );
}
