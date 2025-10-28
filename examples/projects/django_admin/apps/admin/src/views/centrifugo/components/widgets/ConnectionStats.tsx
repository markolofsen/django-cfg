/**
 * Connection Stats Widget
 *
 * Displays connection metrics and status
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, Badge } from '@djangocfg/ui';
import { Wifi, WifiOff, Clock, MessageSquare, Radio } from 'lucide-react';
import { useCentrifugoLiveTestingContext } from '@/contexts/centrifugo';

export const ConnectionStats: React.FC = () => {
  const { isConnected, isConnecting, connectionTime, subscriptions, totalMessagesReceived } =
    useCentrifugoLiveTestingContext();
  const [uptime, setUptime] = useState<string>('--:--:--');

  // Calculate uptime
  useEffect(() => {
    if (!connectionTime || !isConnected) {
      setUptime('--:--:--');
      return;
    }

    const updateUptime = () => {
      const now = new Date();
      const diff = Math.floor((now.getTime() - connectionTime.getTime()) / 1000);

      const hours = Math.floor(diff / 3600);
      const minutes = Math.floor((diff % 3600) / 60);
      const seconds = diff % 60;

      setUptime(
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      );
    };

    updateUptime();
    const interval = setInterval(updateUptime, 1000);

    return () => clearInterval(interval);
  }, [connectionTime, isConnected]);

  const getStatusColor = () => {
    if (isConnecting) return 'bg-yellow-500';
    if (isConnected) return 'bg-green-500';
    return 'bg-red-500';
  };

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...';
    if (isConnected) return 'Connected';
    return 'Disconnected';
  };

  const getStatusIcon = () => {
    if (isConnecting) return <Wifi className="h-4 w-4 animate-pulse" />;
    if (isConnected) return <Wifi className="h-4 w-4" />;
    return <WifiOff className="h-4 w-4" />;
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-semibold text-sm">Connection Status</span>
          </div>
          <Badge
            variant="outline"
            className={`${
              isConnected
                ? 'bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-300 border-green-300 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-950/20 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800'
            }`}
          >
            <div className={`w-2 h-2 rounded-full ${getStatusColor()} mr-2 ${isConnected ? 'animate-pulse' : ''}`} />
            {getStatusText()}
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Uptime */}
          <div className="flex flex-col items-center p-3 rounded-lg bg-muted/30 border border-border">
            <Clock className="h-5 w-5 text-blue-500 mb-1" />
            <span className="text-xs text-muted-foreground mb-1">Uptime</span>
            <span className="text-lg font-mono font-semibold">{uptime}</span>
          </div>

          {/* Messages */}
          <div className="flex flex-col items-center p-3 rounded-lg bg-muted/30 border border-border">
            <MessageSquare className="h-5 w-5 text-purple-500 mb-1" />
            <span className="text-xs text-muted-foreground mb-1">Messages</span>
            <span className="text-lg font-mono font-semibold">{totalMessagesReceived}</span>
          </div>

          {/* Subscriptions */}
          <div className="flex flex-col items-center p-3 rounded-lg bg-muted/30 border border-border">
            <Radio className="h-5 w-5 text-green-500 mb-1" />
            <span className="text-xs text-muted-foreground mb-1">Channels</span>
            <span className="text-lg font-mono font-semibold">{subscriptions.size}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
