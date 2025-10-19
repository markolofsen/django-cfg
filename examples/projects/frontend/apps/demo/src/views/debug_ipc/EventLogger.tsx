/**
 * Event Logger Component
 *
 * Displays real-time log of all IPC events (sent, received, errors).
 * Provides filtering, clearing, and export functionality.
 */

'use client';

import { useState, useMemo } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
  Badge,
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  ScrollArea,
  useToast,
} from '@djangocfg/ui';
import {
  Trash2,
  Download,
  Filter,
  ArrowUp,
  ArrowDown,
  Clock,
  Send,
  MessageSquare,
  AlertCircle,
  Info,
} from 'lucide-react';
import type { LogEntry } from './DebugIPCView';

interface EventLoggerProps {
  logs: LogEntry[];
  onClear: () => void;
}

export function EventLogger({ logs, onClear }: EventLoggerProps) {
  const { toast } = useToast();
  const [filter, setFilter] = useState<string>('all');

  const filteredLogs = useMemo(() => {
    if (filter === 'all') return logs;
    return logs.filter((log) => log.type === filter);
  }, [logs, filter]);

  const handleExport = () => {
    try {
      const exportData = JSON.stringify(filteredLogs, null, 2);
      const blob = new Blob([exportData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ipc-logs-${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);

      toast({
        title: 'Exported',
        description: `Exported ${filteredLogs.length} log entries`,
      });
    } catch (error) {
      toast({
        title: 'Export Failed',
        description: 'Failed to export logs',
        variant: 'destructive',
      });
    }
  };

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'sent':
        return <ArrowUp className="h-4 w-4 text-blue-500" />;
      case 'received':
        return <ArrowDown className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'info':
        return <Info className="h-4 w-4 text-gray-500" />;
      default:
        return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getLogBadge = (type: LogEntry['type']) => {
    switch (type) {
      case 'sent':
        return (
          <Badge variant="outline" className="border-blue-500 text-blue-500">
            Sent
          </Badge>
        );
      case 'received':
        return (
          <Badge variant="outline" className="border-green-500 text-green-500">
            Received
          </Badge>
        );
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'info':
        return <Badge variant="secondary">Info</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3,
    } as Intl.DateTimeFormatOptions);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Event Logger</CardTitle>
            <CardDescription>
              Real-time log of all IPC events ({filteredLogs.length} entries)
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {/* Filter */}
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Events</SelectItem>
                <SelectItem value="sent">Sent Only</SelectItem>
                <SelectItem value="received">Received Only</SelectItem>
                <SelectItem value="error">Errors Only</SelectItem>
                <SelectItem value="info">Info Only</SelectItem>
              </SelectContent>
            </Select>

            {/* Export */}
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>

            {/* Clear */}
            <Button variant="outline" size="sm" onClick={onClear}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[600px] w-full rounded-md border">
          <div className="p-4 space-y-3">
            {filteredLogs.length === 0 ? (
              <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                <div className="flex flex-col items-center gap-2">
                  <MessageSquare className="h-12 w-12 opacity-20" />
                  <p className="text-sm">No events logged yet</p>
                  <p className="text-xs">
                    {filter !== 'all'
                      ? 'Try changing the filter'
                      : 'Start by sending an RPC request'}
                  </p>
                </div>
              </div>
            ) : (
              filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className="rounded-lg border p-3 bg-card hover:bg-accent/50 transition-colors"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      {getLogIcon(log.type)}
                      {getLogBadge(log.type)}
                      {log.method && (
                        <Badge variant="outline" className="font-mono text-xs">
                          {log.method}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {formatTimestamp(log.timestamp)}
                    </div>
                  </div>

                  {/* Data */}
                  <div className="mt-2 rounded bg-muted/50 p-2">
                    <pre className="font-mono text-xs whitespace-pre-wrap break-all overflow-auto max-h-[200px]">
                      {JSON.stringify(log.data, null, 2)}
                    </pre>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
