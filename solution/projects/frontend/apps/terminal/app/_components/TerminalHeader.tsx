'use client';

import { Card, CardContent, Badge } from '@djangocfg/ui-nextjs';
import { Monitor, Clock, Activity, HardDrive, Cpu } from 'lucide-react';
import type { TerminalSessionDetail } from '@lib/api/generated/terminal/_utils/schemas/TerminalSessionDetail.schema';

interface TerminalHeaderProps {
  session: TerminalSessionDetail;
}

export function TerminalHeader({ session }: TerminalHeaderProps) {
  const formatBytes = (bytes: number | undefined | null) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const formatDate = (date: string | undefined | null) => {
    if (!date) return '-';
    return new Date(date).toLocaleString();
  };

  const isConnected = session.status === 'connected';

  return (
    <Card>
      <CardContent className="p-4">
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {/* Host */}
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Host</p>
            <p className="text-sm font-medium truncate">
              {session.electron_hostname || 'Unknown'}
            </p>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Status</p>
            <Badge
              variant={isConnected ? 'default' : 'secondary'}
              className="mt-0.5"
            >
              {session.status}
            </Badge>
          </div>
        </div>

        {/* Connected At */}
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Connected</p>
            <p className="text-sm font-medium">
              {formatDate(session.connected_at)}
            </p>
          </div>
        </div>

        {/* Commands */}
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Commands</p>
            <p className="text-sm font-medium">{session.commands_count || 0}</p>
          </div>
        </div>

        {/* Bytes Sent */}
        <div className="flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Sent</p>
            <p className="text-sm font-medium">{formatBytes(session.bytes_sent)}</p>
          </div>
        </div>

        {/* Bytes Received */}
        <div className="flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Received</p>
            <p className="text-sm font-medium">{formatBytes(session.bytes_received)}</p>
          </div>
        </div>
      </div>
      </CardContent>
    </Card>
  );
}
