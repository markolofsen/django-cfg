/**
 * Dashboard Overview Page
 * Path: /admin
 */

import type { PageWithLayout } from "@djangocfg/layouts";
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge } from '@djangocfg/ui';
import { admin } from '@/core/routes';
import { useRouter } from 'next/router';
import { ArrowRight } from 'lucide-react';

const View: PageWithLayout = () => {
  const router = useRouter();

  // Get all admin routes except the overview page
  const routes = admin.routes.allRoutes.filter(route => route.path !== admin.routes.overview.path);

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to the admin panel. Select a section below to get started.
        </p>
      </div>

      {/* Routes Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {routes.map((route) => {
          const Icon = route.metadata.icon;
          return (
            <Card key={route.path} className="group hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3">
                  {Icon && (
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                  )}
                  <div className="flex-1">
                    <CardTitle className="text-lg">{route.metadata.label}</CardTitle>
                  </div>
                </div>
                {route.metadata.description && (
                  <CardDescription className="mt-2">
                    {route.metadata.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                  onClick={() => router.push(route.path)}
                >
                  Open
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Stats Section */}
      <div className="grid gap-4 md:grid-cols-3 pt-6 border-t">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Sections
            </CardTitle>
            <div className="text-2xl font-bold">{routes.length}</div>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Status
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="default">Active</Badge>
            </div>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Access Level
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Admin</Badge>
            </div>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
};

View.pageConfig = {
  title: 'Dashboard Overview',
  description: 'Admin dashboard overview',
};

View.getLayout = DashboardLayout;

export default View;
