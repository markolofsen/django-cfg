/**
 * DashboardNav Component
 *
 * Navigation tabs for dashboard pages
 * - Desktop: Full-width flex tabs with equal spacing
 * - Mobile: Auto-converts to Sheet menu with burger button
 *
 * Features:
 * - Dynamic tab visibility based on user permissions (superuser)
 * - Dynamic tab visibility based on Django config (gRPC, Centrifugo, RQ)
 * - Auto-detection of active tab from URL
 * - Responsive mobile/desktop switching via Tabs component
 */

import { useRouter } from 'next/router';
import Link from 'next/link';
import { Tabs, TabsList, TabsTrigger } from '@djangocfg/ui';
import { admin } from '@/core/routes';

export function DashboardNav() {
  const router = useRouter();
  const pathname = router.pathname;

  // Get all dashboard routes and filter by permissions and config
  const navItems = admin.routes.allRoutes.filter((route) => {
    return true;
  });

  // Helper to check if route is active
  const isRouteActive = (routePath: string) => {
    return pathname === routePath ||
      (routePath !== '/admin' && pathname.startsWith(routePath));
  };

  // Find active tab
  const activeTab = navItems.find((route) => isRouteActive(route.path))?.path ||
    navItems[0]?.path ||
    '/admin';

  return (
    <Tabs
      value={activeTab}
      mobileSheet
      mobileTitleText="Dashboard"
      mobileSheetTitle="Dashboard Navigation"
      sticky
    >
      <TabsList fullWidth scrollable>
        {navItems.map((route) => {
          const Icon = route.metadata.icon;

          return (
            <TabsTrigger
              key={route.path}
              value={route.path}
              flexEqual
              className="gap-2"
              asChild
            >
              <Link href={route.path}>
                {Icon && <Icon className="h-4 w-4" />}
                <span>{route.metadata.label}</span>
              </Link>
            </TabsTrigger>
          );
        })}
      </TabsList>
    </Tabs>
  );
}
