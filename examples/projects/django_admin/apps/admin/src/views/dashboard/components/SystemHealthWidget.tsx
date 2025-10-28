/**
 * SystemHealthWidget Component
 *
 * Displays overall system health status and individual component health
 *
 * Features:
 * - Overall health percentage with status badge
 * - List of system components with health indicators
 * - Color-coded status (healthy, warning, error, unknown)
 * - Progress bars for component health percentages
 * - Last check timestamps
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Badge, Progress, Skeleton, Alert, AlertDescription } from '@djangocfg/ui';
import { CheckCircle2, AlertCircle, XCircle, HelpCircle } from 'lucide-react';
import moment from 'moment';
import type { SystemHealth } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface SystemHealthWidgetProps {
  health?: SystemHealth;
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

const getStatusIcon = (status: 'healthy' | 'warning' | 'error' | 'unknown') => {
  switch (status) {
    case 'healthy':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'warning':
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    case 'error':
      return <XCircle className="h-4 w-4 text-red-500" />;
    case 'unknown':
    default:
      return <HelpCircle className="h-4 w-4 text-muted-foreground" />;
  }
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

const getStatusColor = (status: 'healthy' | 'warning' | 'error' | 'unknown'): string => {
  switch (status) {
    case 'healthy':
      return 'text-green-500';
    case 'warning':
      return 'text-yellow-500';
    case 'error':
      return 'text-red-500';
    case 'unknown':
    default:
      return 'text-muted-foreground';
  }
};

const formatTimestamp = (timestamp: string): string => {
  try {
    return moment(timestamp).fromNow();
  } catch {
    return timestamp;
  }
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function SystemHealthSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-6 w-32 mb-2" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-6 w-20" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-16" />
            </div>
            <Skeleton className="h-2 w-full" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function SystemHealthWidget({ health, isLoading }: SystemHealthWidgetProps) {
  // Loading state
  if (isLoading) {
    return <SystemHealthSkeleton />;
  }

  // No data
  if (!health) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>No health data available</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>System Health</CardTitle>
            <CardDescription>
              Last check: {formatTimestamp(health.timestamp)}
            </CardDescription>
          </div>
          <Badge variant={getStatusBadgeVariant(health.overall_status)}>
            {health.overall_status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Health Percentage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Health</span>
            <span className="text-sm font-bold">{health.overall_health_percentage}%</span>
          </div>
          <Progress value={health.overall_health_percentage} className="h-2" />
        </div>

        {/* Components List */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium">Components</h4>
          {health.components.map((component, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(component.status)}
                  <span className="text-sm font-medium">{component.component}</span>
                </div>
                <span className={`text-xs font-medium ${getStatusColor(component.status)}`}>
                  {component.status}
                </span>
              </div>

              {/* Health percentage progress bar */}
              {component.health_percentage !== null && component.health_percentage !== undefined && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-muted-foreground">{component.description}</span>
                    <span className="text-xs font-medium">{component.health_percentage}%</span>
                  </div>
                  <Progress value={component.health_percentage} className="h-1.5" />
                </div>
              )}

              {/* Description only (no progress bar) */}
              {(component.health_percentage === null || component.health_percentage === undefined) && (
                <p className="text-xs text-muted-foreground">{component.description}</p>
              )}

              {/* Last check time */}
              <p className="text-xs text-muted-foreground">
                Last check: {formatTimestamp(component.last_check)}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
