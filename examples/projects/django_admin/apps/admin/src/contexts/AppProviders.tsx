import React, { ReactNode } from 'react';
import { SWRConfig } from 'swr';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Main App Providers
 *
 * Wraps the app with SWR configuration and context providers.
 * SWR is already integrated in the generated API clients.
 */
export function AppProviders({ children }: AppProvidersProps) {
  return (
    <SWRConfig
      value={{
        refreshInterval: 0, // Disable auto-refresh by default
        revalidateOnFocus: false, // Don't refetch on window focus
        revalidateOnReconnect: true, // Refetch on network reconnect
        shouldRetryOnError: true,
        errorRetryCount: 1,
        dedupingInterval: 2000, // Dedupe requests within 2 seconds
      }}
    >
      {children}
    </SWRConfig>
  );
}
