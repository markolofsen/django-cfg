/**
 * SystemHealthRadial Component
 *
 * Radial progress chart for system health percentage
 *
 * Features:
 * - Circular progress indicator
 * - Color-coded by health status (green/yellow/red)
 * - Center text showing percentage
 * - Status badge
 * - Responsive design
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Skeleton, Badge } from '@djangocfg/ui';
import { ChartContainer } from '@djangocfg/ui';
import * as Recharts from 'recharts';
import moment from 'moment';

const { RadialBar, RadialBarChart, PolarAngleAxis } = Recharts;
import type { SystemHealth } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface SystemHealthRadialProps {
  health?: SystemHealth;
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

const getHealthColor = (percentage: number): string => {
  if (percentage >= 80) return 'hsl(var(--chart-1))'; // Green
  if (percentage >= 50) return 'hsl(var(--chart-3))'; // Yellow
  return 'hsl(var(--chart-5))'; // Red
};

const getStatusBadgeVariant = (
  status: 'healthy' | 'warning' | 'error' | 'unknown'
): 'default' | 'secondary' | 'destructive' => {
  switch (status) {
    case 'healthy':
      return 'default';
    case 'warning':
      return 'secondary';
    case 'error':
      return 'destructive';
    case 'unknown':
    default:
      return 'secondary';
  }
};

// ─────────────────────────────────────────────────────────────────────────
// Chart Configuration
// ─────────────────────────────────────────────────────────────────────────

const chartConfig = {
  health: {
    label: 'Health',
  },
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function SystemHealthRadialSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40 mb-2" />
        <Skeleton className="h-4 w-56" />
      </CardHeader>
      <CardContent className="flex items-center justify-center">
        <Skeleton className="h-[250px] w-[250px] rounded-full" />
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function SystemHealthRadial({ health, isLoading }: SystemHealthRadialProps) {
  // Loading state
  if (isLoading) {
    return <SystemHealthRadialSkeleton />;
  }

  // No data
  if (!health) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No health data available</p>
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    {
      name: 'health',
      value: health.overall_health_percentage,
      fill: getHealthColor(health.overall_health_percentage),
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>System Health</CardTitle>
            <CardDescription>
              Overall health status
              {health.timestamp && (
                <span className="text-xs ml-2">
                  · Updated {moment(health.timestamp).fromNow()}
                </span>
              )}
            </CardDescription>
          </div>
          <Badge variant={getStatusBadgeVariant(health.overall_status)}>
            {health.overall_status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center pb-8">
        <ChartContainer config={chartConfig} className="h-[250px] w-full">
          <RadialBarChart
            data={chartData}
            startAngle={90}
            endAngle={90 + (health.overall_health_percentage / 100) * 360}
            innerRadius="80%"
            outerRadius="100%"
          >
            <PolarAngleAxis
              type="number"
              domain={[0, 100]}
              angleAxisId={0}
              tick={false}
            />
            <RadialBar
              background
              dataKey="value"
              cornerRadius={10}
              fill={getHealthColor(health.overall_health_percentage)}
            />
            <text
              x="50%"
              y="50%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-foreground"
            >
              <tspan x="50%" dy="-0.5em" fontSize="48" fontWeight="bold">
                {health.overall_health_percentage}%
              </tspan>
              <tspan x="50%" dy="1.5em" fontSize="14" className="fill-muted-foreground">
                System Health
              </tspan>
            </text>
          </RadialBarChart>
        </ChartContainer>

        {/* Component Count Summary */}
        <div className="mt-6 grid grid-cols-3 gap-4 w-full text-center">
          <div>
            <p className="text-2xl font-bold text-green-500">
              {health.components.filter((c) => c.status === 'healthy').length}
            </p>
            <p className="text-xs text-muted-foreground">Healthy</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-yellow-500">
              {health.components.filter((c) => c.status === 'warning').length}
            </p>
            <p className="text-xs text-muted-foreground">Warning</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-red-500">
              {health.components.filter((c) => c.status === 'error').length}
            </p>
            <p className="text-xs text-muted-foreground">Error</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
