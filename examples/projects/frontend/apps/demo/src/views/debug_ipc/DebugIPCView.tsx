/**
 * Debug IPC View
 *
 * Main view component for IPC debugging.
 * Shows connection status, RPC method tester, and event logger.
 */

'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';
import { ConnectionStatus } from './ConnectionStatus';
import { RPCMethodTester } from './RPCMethodTester';
import { EventLogger } from './EventLogger';
import { Activity, Terminal, List } from 'lucide-react';

export interface LogEntry {
  id: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'error' | 'info';
  method?: string;
  data: any;
}

export function DebugIPCView() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = (entry: Omit<LogEntry, 'id' | 'timestamp'>) => {
    setLogs((prev) => [
      {
        ...entry,
        id: `${Date.now()}-${Math.random()}`,
        timestamp: new Date(),
      },
      ...prev,
    ].slice(0, 100)); // Keep last 100 entries
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">IPC Debug Console</h1>
          <p className="text-muted-foreground mt-1">
            Test WebSocket RPC communication with Django backend
          </p>
        </div>
      </div>

      {/* Connection Status Card */}
      <ConnectionStatus onLog={addLog} />

      {/* Main Content */}
      <Tabs defaultValue="tester" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="tester" className="flex items-center gap-2">
            <Terminal className="h-4 w-4" />
            RPC Method Tester
          </TabsTrigger>
          <TabsTrigger value="logger" className="flex items-center gap-2">
            <List className="h-4 w-4" />
            Event Logger
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tester" className="mt-6">
          <RPCMethodTester onLog={addLog} />
        </TabsContent>

        <TabsContent value="logger" className="mt-6">
          <EventLogger logs={logs} onClear={clearLogs} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
