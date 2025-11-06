/**
 * Dashboard Context
 *
 * Provides dashboard state and configuration
 */

import React, { createContext, useContext, ReactNode } from 'react';

interface DjangoConfig {
  grpc?: { enabled: boolean };
  centrifugo?: { enabled: boolean };
  django_rq?: { enabled: boolean };
}

interface DashboardContextValue {
  djangoConfig: DjangoConfig | null;
}

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined);

export function DashboardProvider({ children }: { children: ReactNode }) {
  // Simple default config for solution project
  const djangoConfig: DjangoConfig = {
    grpc: { enabled: false },
    centrifugo: { enabled: false },
    django_rq: { enabled: false },
  };

  return (
    <DashboardContext.Provider value={{ djangoConfig }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboardOverviewContext() {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error('useDashboardOverviewContext must be used within DashboardProvider');
  }
  return context;
}

// Alias for backward compatibility
export const DashboardOverviewProvider = DashboardProvider;
