import type { ReactNode } from 'react';
import type { Metadata } from 'next';
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
 * Wraps all /admin/* pages
 */
export default function AdminLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

