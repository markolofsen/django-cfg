/**
 * UserStatisticsChart Component
 *
 * User statistics visualization with bar chart
 *
 * Features:
 * - Total, Active, New, Superusers counts
 * - Vertical bar chart
 * - Color-coded bars
 * - Interactive tooltips
 * - Responsive design
 */

'use client';

import React from 'react';
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

const { Bar, BarChart, CartesianGrid, XAxis, YAxis } = Recharts;
import type { UserStatistics } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface UserStatisticsChartProps {
  statistics?: UserStatistics;
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Chart Configuration
// ─────────────────────────────────────────────────────────────────────────

const chartConfig = {
  count: {
    label: 'Users',
    color: 'hsl(var(--chart-1))',
  },
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function UserStatisticsChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40 mb-2" />
        <Skeleton className="h-4 w-56" />
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

export function UserStatisticsChart({ statistics, isLoading }: UserStatisticsChartProps) {
  // Loading state
  if (isLoading) {
    return <UserStatisticsChartSkeleton />;
  }

  // No data
  if (!statistics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>User Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No user statistics available</p>
        </CardContent>
      </Card>
    );
  }

  // Transform data for chart
  const chartData = [
    {
      category: 'Total Users',
      count: statistics.total_users,
      fill: 'hsl(var(--chart-1))',
    },
    {
      category: 'Active Users',
      count: statistics.active_users,
      fill: 'hsl(var(--chart-2))',
    },
    {
      category: 'New Users',
      count: statistics.new_users,
      fill: 'hsl(var(--chart-3))',
    },
    {
      category: 'Superusers',
      count: statistics.superusers,
      fill: 'hsl(var(--chart-4))',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Statistics</CardTitle>
        <CardDescription>Breakdown of user accounts</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="category"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              className="text-xs"
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              className="text-xs"
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="count" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
