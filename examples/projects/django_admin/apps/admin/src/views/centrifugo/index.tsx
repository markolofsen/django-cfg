/**
 * Centrifugo Management Dashboard
 *
 * Real-time monitoring and management interface for Centrifugo
 *
 * Features:
 * - Overview statistics and charts
 * - Recent publishes tracking
 * - Channel statistics
 * - Live channel monitoring
 * - Testing tools
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Tabs, TabsList, TabsTrigger, TabsContent, Badge } from '@djangocfg/ui';
import { Activity, List, Database, Radio, TestTube } from 'lucide-react';
import {
  CentrifugoMonitoringProvider,
  CentrifugoAdminApiProvider,
  CentrifugoTestingProvider,
} from '@/contexts/centrifugo';

// Components
import { SystemStatus } from './components/SystemStatus';
import { StatCards } from './components/StatCards';
import { OverviewTab } from './components/OverviewTab';
import { PublishesTab } from './components/PublishesTab';
import { ChannelsTab } from './components/ChannelsTab';
import { LiveChannelsTab } from './components/LiveChannelsTab';
import { TestingTab } from './components/TestingTab';

// Dialogs
import { PublishTestDialog } from './components/dialogs/PublishTestDialog';
import { PublishWithLoggingDialog } from './components/dialogs/PublishWithLoggingDialog';
import { SendAckDialog } from './components/dialogs/SendAckDialog';
import { ChannelHistoryDialog } from './components/dialogs/ChannelHistoryDialog';
import { ChannelPresenceDialog } from './components/dialogs/ChannelPresenceDialog';

// Types
import type { TabType } from './types';

// ─────────────────────────────────────────────────────────────────────────
// View Content Component
// ─────────────────────────────────────────────────────────────────────────

const CentrifugoViewContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  return (
    <div className="space-y-6">
      {/* System Status */}
      <SystemStatus />

      {/* Statistics Cards */}
      <StatCards />

      {/* Tab Navigation */}
      <Card>
        <CardHeader>
          <CardTitle>Centrifugo Monitor Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabType)}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                <span>Overview</span>
              </TabsTrigger>
              <TabsTrigger value="publishes" className="flex items-center gap-2">
                <List className="h-4 w-4" />
                <span>Recent Publishes</span>
              </TabsTrigger>
              <TabsTrigger value="channels" className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                <span>Channels</span>
              </TabsTrigger>
              <TabsTrigger value="live-channels" className="flex items-center gap-2">
                <Radio className="h-4 w-4" />
                <span>Live Channels</span>
              </TabsTrigger>
              <TabsTrigger value="testing" className="flex items-center gap-2">
                <TestTube className="h-4 w-4" />
                <span>Live Testing</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <OverviewTab />
            </TabsContent>

            <TabsContent value="publishes" className="mt-6">
              <PublishesTab />
            </TabsContent>

            <TabsContent value="channels" className="mt-6">
              <ChannelsTab />
            </TabsContent>

            <TabsContent value="live-channels" className="mt-6">
              <LiveChannelsTab />
            </TabsContent>

            <TabsContent value="testing" className="mt-6">
              <TestingTab />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Dialogs (Event-driven) */}
      <PublishTestDialog />
      <PublishWithLoggingDialog />
      <SendAckDialog />
      <ChannelHistoryDialog />
      <ChannelPresenceDialog />
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────
// Main View Component (with Providers)
// ─────────────────────────────────────────────────────────────────────────

export const CentrifugoView: React.FC = () => {
  return (
    <CentrifugoMonitoringProvider>
      <CentrifugoAdminApiProvider>
        <CentrifugoTestingProvider>
          <CentrifugoViewContent />
        </CentrifugoTestingProvider>
      </CentrifugoAdminApiProvider>
    </CentrifugoMonitoringProvider>
  );
};

export default CentrifugoView;
