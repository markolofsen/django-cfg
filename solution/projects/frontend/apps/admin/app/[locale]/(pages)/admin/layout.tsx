import type { ReactNode } from 'react';
import type { Metadata } from 'next';
import { generateMetadata } from '@core/metadata';

import { AdminLayout } from '@layouts/AdminLayout';

export const metadata: Metadata = generateMetadata({
  title: {
    default: 'Admin Dashboard',
    template: '%s | Admin Dashboard',
  },
  description: 'Django CFG Admin Dashboard - System management and monitoring',
});

/**
 * Admin shell for `/admin/*` — the private shell with an admin sidebar menu
 * (AdminLayout wraps BasePrivateLayout). Providers live once in
 * `[locale]/layout.tsx`.
 */
export default function AdminRouteLayout({ children }: { children: ReactNode }) {
  return <AdminLayout>{children}</AdminLayout>;
}

