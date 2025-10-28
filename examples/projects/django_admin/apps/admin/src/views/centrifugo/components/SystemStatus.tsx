/**
 * System Status Component
 *
 * Displays Centrifugo health check and connection status
 */

'use client';

import React from 'react';
import { Alert, AlertDescription, AlertTitle, Badge, Skeleton } from '@djangocfg/ui';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useCentrifugoMonitoringContext } from '@/contexts/centrifugo';

export const SystemStatus: React.FC = () => {
  const { health, isLoadingHealth, healthError } = useCentrifugoMonitoringContext();

  // Loading state
  if (isLoadingHealth) {
    return (
      <Alert>
        <Skeleton className="h-4 w-full" />
      </Alert>
    );
  }

  // Error state
  if (healthError) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Health Check Failed</AlertTitle>
        <AlertDescription>
          Unable to connect to Centrifugo monitoring service.
        </AlertDescription>
      </Alert>
    );
  }

  // No data
  if (!health) {
    return null;
  }

  // Success state
  const isHealthy = health.status === 'healthy';

  return (
    <Alert variant={isHealthy ? 'default' : 'destructive'}>
      {isHealthy ? (
        <CheckCircle className="h-4 w-4 text-green-600" />
      ) : (
        <AlertCircle className="h-4 w-4" />
      )}
      <AlertTitle className="flex items-center gap-2">
        System Status
        {isHealthy ? (
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Healthy
          </Badge>
        ) : (
          <Badge variant="destructive">Issues Detected</Badge>
        )}
      </AlertTitle>
      <AlertDescription className="mt-2 space-y-2">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <span className="font-medium">Wrapper URL:</span>
            <span className="text-sm text-muted-foreground">{health.wrapper_url || 'Not configured'}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">API Key:</span>
            {health.has_api_key ? (
              <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Configured
              </Badge>
            ) : (
              <Badge variant="destructive">Not configured</Badge>
            )}
          </div>
        </div>
        <div className="text-xs text-muted-foreground">
          Last checked: {new Date(health.timestamp).toLocaleString()}
        </div>
      </AlertDescription>
    </Alert>
  );
};
