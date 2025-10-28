/**
 * AdminNav Component
 *
 * Compact horizontal navigation tabs for admin routes
 * Automatically generated from admin routes
 * Designed to be embedded in Django iframe
 *
 * Uses Tabs component from @djangocfg/ui for consistent styling
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
    <div className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mb-4">
      <div className="container max-w-screen-2xl">
        <Tabs value={activeTab}>
          <TabsList className="h-14 w-full justify-start rounded-none border-0 bg-transparent p-0">
            {navItems.map((route) => {
              const Icon = route.metadata.icon;

              return (
                <TabsTrigger
                  key={route.path}
                  value={route.path}
                  className="h-14 gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-muted/50"
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
      </div>
    </div>
  );
}
