/**
 * Connection Status Component
 *
 * Displays WebSocket connection status and provides connect/disconnect controls.
 */

'use client';

import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from '@djangocfg/ui';
import { useWSRPC } from '@/rpc';
import { Wifi, WifiOff, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import type { LogEntry } from './DebugIPCView';

interface ConnectionStatusProps {
  onLog: (entry: Omit<LogEntry, 'id' | 'timestamp'>) => void;
}

export function ConnectionStatus({ onLog }: ConnectionStatusProps) {
  const { isConnected, isConnecting, connectionState, connect, disconnect } = useWSRPC();

  const handleConnect = async () => {
    onLog({
      type: 'info',
      data: { message: 'Initiating connection...' },
    });
    try {
      await connect();
      onLog({
        type: 'info',
        data: { message: 'Connected successfully' },
      });
    } catch (error) {
      onLog({
        type: 'error',
        data: { message: 'Connection failed', error: String(error) },
      });
    }
  };

  const handleDisconnect = () => {
    onLog({
      type: 'info',
      data: { message: 'Disconnecting...' },
    });
    disconnect();
    onLog({
      type: 'info',
      data: { message: 'Disconnected' },
    });
  };

  const getStatusIcon = () => {
    if (isConnected) return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    if (isConnecting) return <Clock className="h-5 w-5 text-yellow-500 animate-pulse" />;
    return <XCircle className="h-5 w-5 text-red-500" />;
  };

  const getStatusBadge = () => {
    if (isConnected) {
      return (
        <Badge variant="default" className="bg-green-500 hover:bg-green-600">
          <Wifi className="h-3 w-3 mr-1" />
          Connected
        </Badge>
      );
    }
    if (isConnecting) {
      return (
        <Badge variant="secondary" className="bg-yellow-500 hover:bg-yellow-600">
          <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
          Connecting...
        </Badge>
      );
    }
    return (
      <Badge variant="destructive">
        <WifiOff className="h-3 w-3 mr-1" />
        Disconnected
      </Badge>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <CardTitle>WebSocket Connection</CardTitle>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Connection Details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Status:</span>
              <span className="ml-2 font-medium">{connectionState || 'Unknown'}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Auto-reconnect:</span>
              <span className="ml-2 font-medium">Enabled</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              onClick={handleConnect}
              disabled={isConnected || isConnecting}
              variant="default"
              size="sm"
            >
              <Wifi className="h-4 w-4 mr-2" />
              Connect
            </Button>
            <Button
              onClick={handleDisconnect}
              disabled={!isConnected && !isConnecting}
              variant="outline"
              size="sm"
            >
              <WifiOff className="h-4 w-4 mr-2" />
              Disconnect
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
