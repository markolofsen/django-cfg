/**
 * WebSocket Status Indicator Component
 * Shows connection status of WebSocket RPC client
 */

'use client';

import React from 'react';
import { Wifi, WifiOff, Loader2 } from 'lucide-react';
import { Badge } from '@djangocfg/ui';
import { useWSRPC } from '@/rpc';

export function WebSocketStatus() {
  const { isConnected, isConnecting, error } = useWSRPC();

  // Don't show if still connecting on initial load
  if (!isConnected && !error && !isConnecting) {
    return null;
  }

  if (isConnecting) {
    return (
      <Badge
        variant="outline"
        className="flex items-center gap-1.5 text-yellow-600 border-yellow-600/30 bg-yellow-50 dark:bg-yellow-950/20"
      >
        <Loader2 className="h-3 w-3 animate-spin" />
        <span className="text-xs">Connecting</span>
      </Badge>
    );
  }

  if (error || !isConnected) {
    return (
      <Badge
        variant="outline"
        className="flex items-center gap-1.5 text-red-600 border-red-600/30 bg-red-50 dark:bg-red-950/20"
        title={error?.message || 'WebSocket disconnected'}
      >
        <WifiOff className="h-3 w-3" />
        <span className="text-xs">Offline</span>
      </Badge>
    );
  }

  return (
    <Badge
      variant="outline"
      className="flex items-center gap-1.5 text-green-600 border-green-600/30 bg-green-50 dark:bg-green-950/20"
    >
      <Wifi className="h-3 w-3" />
      <span className="text-xs">Online</span>
    </Badge>
  );
}