/**
 * SystemMetricsPanel Component
 *
 * Displays system performance metrics with visual indicators
 *
 * Features:
 * - CPU, Memory, Disk usage with progress bars
 * - Network in/out bandwidth
 * - Response time
 * - System uptime
 * - Color-coded thresholds (green < 70%, yellow 70-90%, red > 90%)
 * - Responsive grid layout
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Progress, Skeleton, Badge } from '@djangocfg/ui';
import { Cpu, HardDrive, Activity, Network, Clock, Zap } from 'lucide-react';
import type { SystemMetrics } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface SystemMetricsPanelProps {
  metrics?: SystemMetrics;
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

const getUsageColor = (usage: number): string => {
  if (usage >= 90) return 'text-red-500';
  if (usage >= 70) return 'text-yellow-500';
  return 'text-green-500';
};

const getUsageBadgeVariant = (usage: number): 'default' | 'secondary' | 'destructive' => {
  if (usage >= 90) return 'destructive';
  if (usage >= 70) return 'secondary';
  return 'default';
};

// ─────────────────────────────────────────────────────────────────────────
// Metric Item Component
// ─────────────────────────────────────────────────────────────────────────

interface MetricItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  percentage?: number;
  showProgress?: boolean;
}

function MetricItem({ icon, label, value, percentage, showProgress = false }: MetricItemProps) {
  const displayValue = typeof value === 'number' ? `${value}%` : value;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <div className="text-muted-foreground">{icon}</div>
        <span className="text-sm font-medium">{label}</span>
      </div>

      {showProgress && typeof percentage === 'number' ? (
        <>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold">{displayValue}</span>
            <Badge variant={getUsageBadgeVariant(percentage)} className="ml-2">
              {percentage >= 90 ? 'Critical' : percentage >= 70 ? 'High' : 'Normal'}
            </Badge>
          </div>
          <Progress value={percentage} className="h-2" />
        </>
      ) : (
        <span className="text-2xl font-bold">{displayValue}</span>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function SystemMetricsSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40 mb-2" />
        <Skeleton className="h-4 w-56" />
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-2 w-full" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function SystemMetricsPanel({ metrics, isLoading }: SystemMetricsPanelProps) {
  // Loading state
  if (isLoading) {
    return <SystemMetricsSkeleton />;
  }

  // No data
  if (!metrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No metrics data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Metrics</CardTitle>
        <CardDescription>Real-time system performance</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2">
          {/* CPU Usage */}
          <MetricItem
            icon={<Cpu className="h-4 w-4" />}
            label="CPU Usage"
            value={metrics.cpu_usage}
            percentage={metrics.cpu_usage}
            showProgress
          />

          {/* Memory Usage */}
          <MetricItem
            icon={<Activity className="h-4 w-4" />}
            label="Memory Usage"
            value={metrics.memory_usage}
            percentage={metrics.memory_usage}
            showProgress
          />

          {/* Disk Usage */}
          <MetricItem
            icon={<HardDrive className="h-4 w-4" />}
            label="Disk Usage"
            value={metrics.disk_usage}
            percentage={metrics.disk_usage}
            showProgress
          />

          {/* Network In */}
          <MetricItem
            icon={<Network className="h-4 w-4" />}
            label="Network In"
            value={metrics.network_in}
          />

          {/* Network Out */}
          <MetricItem
            icon={<Network className="h-4 w-4" />}
            label="Network Out"
            value={metrics.network_out}
          />

          {/* Response Time */}
          <MetricItem
            icon={<Zap className="h-4 w-4" />}
            label="Response Time"
            value={metrics.response_time}
          />

          {/* Uptime - spans 2 columns on larger screens */}
          <div className="sm:col-span-2">
            <MetricItem
              icon={<Clock className="h-4 w-4" />}
              label="System Uptime"
              value={metrics.uptime}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
