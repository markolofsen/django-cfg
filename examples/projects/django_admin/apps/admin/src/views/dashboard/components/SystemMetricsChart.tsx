/**
 * SystemMetricsChart Component
 *
 * Real-time system metrics visualization with area chart
 *
 * Features:
 * - CPU, Memory, Disk usage trends
 * - Area chart with smooth curves
 * - Color-coded lines
 * - Interactive tooltips
 * - Legend
 * - Responsive design
 */

'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Skeleton } from '@djangocfg/ui';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from '@djangocfg/ui';
import * as Recharts from 'recharts';

const { Area, AreaChart, CartesianGrid, XAxis, YAxis } = Recharts;
import type { SystemMetrics } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface SystemMetricsChartProps {
  metrics?: SystemMetrics;
  isLoading?: boolean;
  historicalData?: SystemMetrics[];
}

// ─────────────────────────────────────────────────────────────────────────
// Chart Configuration
// ─────────────────────────────────────────────────────────────────────────

const chartConfig = {
  cpu: {
    label: 'CPU Usage',
    color: 'hsl(var(--chart-1))',
  },
  memory: {
    label: 'Memory Usage',
    color: 'hsl(var(--chart-2))',
  },
  disk: {
    label: 'Disk Usage',
    color: 'hsl(var(--chart-3))',
  },
};

// ─────────────────────────────────────────────────────────────────────────
// Mock Data Generator (for demo purposes)
// ─────────────────────────────────────────────────────────────────────────

function generateMockHistoricalData(currentMetrics?: SystemMetrics) {
  if (!currentMetrics) {
    return [];
  }

  const data = [];
  const now = Date.now();
  const interval = 5 * 60 * 1000; // 5 minutes

  // Generate 12 data points (1 hour of data)
  for (let i = 11; i >= 0; i--) {
    const timestamp = new Date(now - i * interval);
    const hours = timestamp.getHours();
    const minutes = timestamp.getMinutes();
    const time = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;

    // Add some variance to make it look realistic
    const variance = () => Math.random() * 10 - 5;

    data.push({
      time,
      cpu: Math.max(0, Math.min(100, currentMetrics.cpu_usage + variance())),
      memory: Math.max(0, Math.min(100, currentMetrics.memory_usage + variance())),
      disk: Math.max(0, Math.min(100, currentMetrics.disk_usage + variance())),
    });
  }

  return data;
}

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function SystemMetricsChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48 mb-2" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-[300px] w-full" />
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function SystemMetricsChart({
  metrics,
  isLoading,
  historicalData,
}: SystemMetricsChartProps) {
  // Loading state
  if (isLoading) {
    return <SystemMetricsChartSkeleton />;
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

  // Use provided historical data or generate mock data
  const chartData = useMemo(() => {
    return historicalData && historicalData.length > 0
      ? historicalData.map((m, i) => ({
          time: `T-${historicalData.length - i}`,
          cpu: m.cpu_usage,
          memory: m.memory_usage,
          disk: m.disk_usage,
        }))
      : generateMockHistoricalData(metrics);
  }, [metrics, historicalData]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Metrics</CardTitle>
        <CardDescription>Resource usage and performance indicators</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Additional Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Network In</p>
            <p className="text-lg font-semibold">{metrics.network_in}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Network Out</p>
            <p className="text-lg font-semibold">{metrics.network_out}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Response Time</p>
            <p className="text-lg font-semibold">{metrics.response_time}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Uptime</p>
            <p className="text-lg font-semibold">{metrics.uptime}</p>
          </div>
        </div>

        {/* Usage Trend Chart */}
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-cpu)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--color-cpu)" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-memory)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--color-memory)" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorDisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-disk)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--color-disk)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              className="text-xs"
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              className="text-xs"
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Area
              type="monotone"
              dataKey="cpu"
              stroke="var(--color-cpu)"
              fill="url(#colorCpu)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="memory"
              stroke="var(--color-memory)"
              fill="url(#colorMemory)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="disk"
              stroke="var(--color-disk)"
              fill="url(#colorDisk)"
              strokeWidth={2}
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
