/**
 * DashboardLayout Component
 *
 * Layout wrapper for dashboard pages
 * Features:
 * - Horizontal tab navigation with grid layout
 * - Sticky header
 * - Responsive container
 * - Auto-detection of user permissions
 * - Includes DashboardOverviewProvider for config-based tab filtering
 *
 * Usage:
 * ```tsx
 * import { DashboardLayout } from '@/layouts/DashboardLayout';
 *
 * export default function DashboardPage() {
 *   return (
 *     <DashboardLayout>
 *       <YourContent />
 *     </DashboardLayout>
 *   );
 * }
 * ```
 */

import type { ReactElement, ReactNode } from 'react';
import { DashboardNav } from './DashboardNav';

interface DashboardLayoutProps {
  children?: ReactNode;
}

export function DashboardLayout(
  pageOrProps: ReactElement | DashboardLayoutProps
) {
  // Support both usage patterns:
  // 1. getLayout = DashboardLayout (page passed as first argument)
  // 2. <DashboardLayout>{children}</DashboardLayout> (props object)

  const children = pageOrProps && typeof pageOrProps === 'object' && 'type' in pageOrProps
    ? pageOrProps
    : (pageOrProps as DashboardLayoutProps).children;

  return (
    <div className="relative flex flex-col min-h-screen">
      {/* Navigation */}
      <DashboardNav />

      {/* Main Content */}
      <main className="flex-1" id="main-content" role="main">
        {children}
      </main>
    </div>
  );
}
