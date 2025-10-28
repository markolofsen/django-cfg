/**
 * AppStatsTab Component
 *
 * Application-specific statistics tab
 *
 * Features:
 * - Application statistics cards
 * - Per-app metrics
 * - Statistics breakdown
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Skeleton, Alert, AlertDescription } from '@djangocfg/ui';
import { Package, AlertCircle } from 'lucide-react';
import type { AppStatistics } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface AppStatsTabProps {
  appStatistics?: AppStatistics[];
  isLoadingAppStatistics?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function AppStatCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40 mb-2" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function AppStatsTab({
  appStatistics,
  isLoadingAppStatistics,
}: AppStatsTabProps) {
  // Loading state
  if (isLoadingAppStatistics) {
    return (
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <AppStatCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  // No data
  if (!appStatistics || appStatistics.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          No application statistics available. This may indicate that no django-cfg apps are enabled or configured.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight mb-2">Application Statistics</h2>
        <p className="text-muted-foreground">
          Statistics for all enabled django-cfg applications
        </p>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {appStatistics.map((app, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    {app.app_name}
                  </CardTitle>
                  <CardDescription className="mt-1">
                    Application metrics
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {app.statistics && typeof app.statistics === 'object' ? (
                  Object.entries(app.statistics).map(([appKey, appValue]) => {
                    // Check if value is an object with nested data
                    if (typeof appValue === 'object' && appValue !== null) {
                      const appData = appValue as any;
                      return (
                        <div key={appKey} className="border-l-2 border-primary/20 pl-3 space-y-2">
                          <div className="font-medium text-sm">
                            {appData.name || appKey.replace(/_/g, ' ')}
                          </div>
                          <div className="space-y-1">
                            {appData.model_count !== undefined && (
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-muted-foreground">Models</span>
                                <span className="font-medium">{appData.model_count}</span>
                              </div>
                            )}
                            {appData.total_records !== undefined && (
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-muted-foreground">Total Records</span>
                                <span className="font-medium">{appData.total_records.toLocaleString()}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    }
                    // Simple key-value
                    return (
                      <div key={appKey} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground capitalize">
                          {appKey.replace(/_/g, ' ')}
                        </span>
                        <span className="font-medium">
                          {typeof appValue === 'number'
                            ? appValue.toLocaleString()
                            : String(appValue)}
                        </span>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-sm text-muted-foreground">
                    No statistics available
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
