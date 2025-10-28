/**
 * Testing Tab Component
 *
 * Provides testing tools for Centrifugo
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '@djangocfg/ui';
import { Send, Database, CheckCircle, Play } from 'lucide-react';
import {
  emitOpenPublishTestDialog,
  emitOpenPublishWithLoggingDialog,
  emitOpenSendAckDialog,
} from '../events';
import { CentrifugoLiveTestingProvider, useCentrifugoLiveTestingContext } from '@/contexts/centrifugo';
import { QuickScenarios } from './widgets/QuickScenarios';
import { EventLogViewer } from './widgets/EventLogViewer';
import { LiveSubscriptionManager } from './widgets/LiveSubscriptionManager';
import { ConnectionStats } from './widgets/ConnectionStats';

const TestingTabContent: React.FC = () => {
  const { isConnected, isConnecting, connect, disconnect } = useCentrifugoLiveTestingContext();

  return (
    <div className="space-y-6">
      {/* Connection Stats + Control */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <ConnectionStats />
        </div>
        <Card>
          <CardContent className="p-4 flex flex-col items-center justify-center h-full gap-3">
            <p className="text-sm text-center text-muted-foreground">
              {isConnected
                ? 'Connected to WebSocket server'
                : 'Start testing real-time features'}
            </p>
            <Button
              onClick={isConnected ? disconnect : connect}
              disabled={isConnecting}
              variant={isConnected ? 'destructive' : 'default'}
              size="lg"
              className="w-full"
            >
              <Play className="h-4 w-4 mr-2" />
              {isConnecting ? 'Connecting...' : isConnected ? 'Disconnect' : 'Connect'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Test Scenarios */}
      <QuickScenarios />

      {/* Live Subscription Manager */}
      <LiveSubscriptionManager />

      {/* Event Log Viewer */}
      <EventLogViewer />

      {/* Traditional Testing Tools */}
      <Card>
        <CardHeader>
          <CardTitle>Advanced Testing Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Publish Test */}
            <Card>
              <CardContent className="p-6">
                <Send className="h-8 w-8 text-purple-500 mb-4" />
                <h3 className="font-semibold mb-2">Publish Test</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Send a test message to a channel with optional ACK tracking
                </p>
                <Button onClick={() => emitOpenPublishTestDialog()} className="w-full">
                  Open Test Publisher
                </Button>
              </CardContent>
            </Card>

            {/* Publish with Logging */}
            <Card>
              <CardContent className="p-6">
                <Database className="h-8 w-8 text-blue-500 mb-4" />
                <h3 className="font-semibold mb-2">Publish with Logging</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Send a message and save to database for tracking
                </p>
                <Button onClick={() => emitOpenPublishWithLoggingDialog()} className="w-full">
                  Open Logger
                </Button>
              </CardContent>
            </Card>

            {/* Send ACK */}
            <Card>
              <CardContent className="p-6">
                <CheckCircle className="h-8 w-8 text-green-500 mb-4" />
                <h3 className="font-semibold mb-2">Send ACK</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Manually send acknowledgment for a message
                </p>
                <Button onClick={() => emitOpenSendAckDialog()} className="w-full">
                  Send ACK
                </Button>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* Usage Guide */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-semibold mb-2">Live Testing</h4>
              <p className="text-muted-foreground">
                Connect to the WebSocket server to test real-time features. Use Quick Scenarios for
                one-click testing, or manually subscribe to channels and publish messages. All events
                are logged in real-time for debugging.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Publish Test</h4>
              <p className="text-muted-foreground">
                Use this tool to send test messages to specific channels. You can enable ACK tracking
                to monitor message delivery confirmations.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Publish with Logging</h4>
              <p className="text-muted-foreground">
                Similar to Publish Test, but creates a CentrifugoLog record in the database for
                persistent tracking and monitoring.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Send ACK</h4>
              <p className="text-muted-foreground">
                Manually send an acknowledgment for a specific message. Useful for testing ACK
                handling and debugging delivery issues.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export const TestingTab: React.FC = () => {
  return (
    <CentrifugoLiveTestingProvider>
      <TestingTabContent />
    </CentrifugoLiveTestingProvider>
  );
};
