import type { ReactNode } from 'react';
import type { Metadata } from 'next';
import { SWRConfig } from 'swr';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: {
    default: 'Admin Dashboard',
    template: '%s | Admin Dashboard',
  },
  description: 'Django CFG Admin Dashboard - System management and monitoring',
});

/**
 * Admin Layout
 * Wraps all /admin/* pages with necessary providers
 * The actual AdminLayout component is applied by AppLayout based on pathname
 */
export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
        refreshInterval: 0,
        dedupingInterval: 10000,
      }}
    >
      {children}
    </SWRConfig>
  );
}

