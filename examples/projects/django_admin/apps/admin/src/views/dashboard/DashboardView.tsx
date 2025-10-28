/**
 * DashboardView Component
 *
 * Main dashboard page with tab-based navigation
 *
 * Tabs:
 * 1. Overview - System overview with stat cards and health
 * 2. Users - User statistics and management
 * 3. System - Detailed system health, metrics, and activity
 * 4. App Stats - Application-specific statistics
 *
 * Features:
 * - Tab-based navigation (matching old dashboard structure)
 * - SWR data fetching with auto-caching
 * - Responsive grid layout
 * - Loading states for all sections
 * - Error handling
 * - Manual refresh capability
 */

'use client';

import React from 'react';
import { Button, Alert, AlertDescription, AlertTitle, Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';
import { RefreshCw, AlertTriangle, LayoutDashboard, Users, Activity, BarChart3, TrendingUp, Terminal, Globe } from 'lucide-react';
import { useAuth } from '@djangocfg/layouts';
import {
  DashboardStatisticsProvider,
  DashboardSystemProvider,
  DashboardActivityProvider,
  DashboardChartsProvider,
  DashboardCommandsProvider,
  DashboardZonesProvider,
  useDashboardStatisticsContext,
  useDashboardSystemContext,
  useDashboardActivityContext,
  useDashboardChartsContext,
  useDashboardCommandsContext,
  useDashboardZonesContext,
} from '@/contexts/dashboard';

// Tab components
import { OverviewTab } from './tabs/OverviewTab';
import { UsersTab } from './tabs/UsersTab';
import { SystemTab } from './tabs/SystemTab';
import { AppStatsTab } from './tabs/AppStatsTab';
import { ChartsTab } from './tabs/ChartsTab';
import { CommandsTab } from './tabs/CommandsTab';
import { ZonesTab } from './tabs/ZonesTab';

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

function DashboardViewInner() {
  // Auth context - check if user is superuser
  const { user } = useAuth();
  const isSuperuser = user?.is_superuser ?? false;

  // Statistics context
  const {
    cards: statCards,
    isLoadingCards: isLoadingStatCards,
    cardsError: statCardsError,
    users: userStatistics,
    isLoadingUsers: isLoadingUserStatistics,
    usersError: userStatisticsError,
    apps: appStatistics,
    isLoadingApps: isLoadingAppStatistics,
    appsError: appStatisticsError,
    refreshAll: refreshStatistics,
  } = useDashboardStatisticsContext();

  // System context
  const {
    health: systemHealth,
    isLoadingHealth: isLoadingSystemHealth,
    healthError: systemHealthError,
    metrics: systemMetrics,
    isLoadingMetrics: isLoadingSystemMetrics,
    metricsError: systemMetricsError,
    refreshAll: refreshSystem,
  } = useDashboardSystemContext();

  // Activity context
  const {
    recentActivity,
    isLoadingRecentActivity,
    recentActivityError,
    quickActions,
    isLoadingQuickActions,
    quickActionsError,
    refreshAll: refreshActivity,
  } = useDashboardActivityContext();

  // Charts context
  const {
    refreshAll: refreshCharts,
  } = useDashboardChartsContext();

  // Commands context
  const {
    refreshAll: refreshCommands,
  } = useDashboardCommandsContext();

  // Zones context
  const {
    refreshAll: refreshZones,
  } = useDashboardZonesContext();

  // Refresh all data
  const handleRefreshAll = async () => {
    await Promise.all([
      refreshStatistics(),
      refreshSystem(),
      refreshActivity(),
      refreshCharts(),
      refreshCommands(),
      refreshZones(),
    ]);
  };

  // Check if any errors occurred
  const hasErrors =
    statCardsError ||
    systemHealthError ||
    systemMetricsError ||
    recentActivityError ||
    quickActionsError ||
    userStatisticsError ||
    appStatisticsError;

  // Check if all loading
  const isLoading =
    isLoadingStatCards &&
    isLoadingSystemHealth &&
    isLoadingSystemMetrics &&
    isLoadingRecentActivity &&
    isLoadingQuickActions &&
    isLoadingUserStatistics &&
    isLoadingAppStatistics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's your system overview.
          </p>
        </div>
        <Button
          onClick={handleRefreshAll}
          disabled={isLoading}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Global Error Alert */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error Loading Dashboard Data</AlertTitle>
          <AlertDescription>
            Some dashboard components failed to load. Please try refreshing.
          </AlertDescription>
        </Alert>
      )}

      {/* Tabs Navigation */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className={`grid w-full ${isSuperuser ? 'grid-cols-7' : 'grid-cols-6'} gap-2`}>
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <LayoutDashboard className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            System
          </TabsTrigger>
          <TabsTrigger value="app-stats" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Apps
          </TabsTrigger>
          <TabsTrigger value="charts" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Charts
          </TabsTrigger>
          {isSuperuser && (
            <TabsTrigger value="commands" className="flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              Commands
            </TabsTrigger>
          )}
          <TabsTrigger value="zones" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Zones
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <OverviewTab
            statCards={statCards}
            isLoadingStatCards={isLoadingStatCards}
            systemHealth={systemHealth}
            isLoadingSystemHealth={isLoadingSystemHealth}
            quickActions={quickActions}
            isLoadingQuickActions={isLoadingQuickActions}
            systemMetrics={systemMetrics}
            isLoadingSystemMetrics={isLoadingSystemMetrics}
          />
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <UsersTab
            userStatistics={userStatistics}
            isLoadingUserStatistics={isLoadingUserStatistics}
            recentActivity={recentActivity}
            isLoadingRecentActivity={isLoadingRecentActivity}
          />
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          <SystemTab
            systemHealth={systemHealth}
            isLoadingSystemHealth={isLoadingSystemHealth}
            systemMetrics={systemMetrics}
            isLoadingSystemMetrics={isLoadingSystemMetrics}
            recentActivity={recentActivity}
            isLoadingRecentActivity={isLoadingRecentActivity}
          />
        </TabsContent>

        {/* App Stats Tab */}
        <TabsContent value="app-stats" className="space-y-6">
          <AppStatsTab
            appStatistics={appStatistics}
            isLoadingAppStatistics={isLoadingAppStatistics}
          />
        </TabsContent>

        {/* Charts Tab */}
        <TabsContent value="charts" className="space-y-6">
          <ChartsTab />
        </TabsContent>

        {/* Commands Tab - Only for superusers */}
        {isSuperuser && (
          <TabsContent value="commands" className="space-y-6">
            <CommandsTab />
          </TabsContent>
        )}

        {/* Zones Tab */}
        <TabsContent value="zones" className="space-y-6">
          <ZonesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Main Component with Providers
// ─────────────────────────────────────────────────────────────────────────

export function DashboardView() {
  return (
    <DashboardStatisticsProvider>
      <DashboardSystemProvider>
        <DashboardActivityProvider>
          <DashboardChartsProvider>
            <DashboardCommandsProvider>
              <DashboardZonesProvider>
                <DashboardViewInner />
              </DashboardZonesProvider>
            </DashboardCommandsProvider>
          </DashboardChartsProvider>
        </DashboardActivityProvider>
      </DashboardSystemProvider>
    </DashboardStatisticsProvider>
  );
}
