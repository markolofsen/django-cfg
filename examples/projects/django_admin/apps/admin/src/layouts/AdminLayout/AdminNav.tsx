/**
 * AdminNav Component
 *
 * Responsive navigation for admin routes
 * - Desktop: Full-width flex tabs with equal spacing
 * - Mobile: Auto-converts to Sheet menu with burger button
 *
 * Automatically generated from admin routes
 * Designed to be embedded in Django iframe
 */

import { useRouter } from 'next/router';
import Link from 'next/link';
import { Tabs, TabsList, TabsTrigger } from '@djangocfg/ui';
import { admin } from '@/core/routes';

export function AdminNav() {
  const router = useRouter();
  const pathname = router.pathname;

  // Get all admin routes
  const navItems = admin.routes.allRoutes;

  // Find active tab
  const activeTab = navItems.find(
    (route) =>
      pathname === route.path ||
      (route.path !== '/admin' && pathname.startsWith(route.path))
  )?.path || navItems[0]?.path || '/admin';

  return (
    <Tabs
      value={activeTab}
      mobileSheet
      mobileTitleText="Admin Panel"
      mobileSheetTitle="Navigation"
      sticky
    >
      <TabsList fullWidth>
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
