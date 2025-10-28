/**
 * Event Log Viewer Component
 *
 * Displays real-time events from Centrifugo WebSocket connection
 */

'use client';

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge, ScrollArea, Input, Switch, ToggleGroup, ToggleGroupItem } from '@djangocfg/ui';
import { Activity, Trash2, Download, Search, Filter } from 'lucide-react';
import { useCentrifugoLiveTestingContext, type CentrifugoEvent } from '@/contexts/centrifugo';

export const EventLogViewer: React.FC = () => {
  const { events, clearEvents } = useCentrifugoLiveTestingContext();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<CentrifugoEvent['type'][]>([]);

  // Auto-scroll to bottom when new events arrive (only if enabled)
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, autoScroll]);

  // Filter events
  const filteredEvents = useMemo(() => {
    let filtered = [...events].reverse(); // Reverse to show newest at bottom

    // Filter by type
    if (selectedTypes.length > 0) {
      filtered = filtered.filter((event) => selectedTypes.includes(event.type));
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (event) =>
          event.message.toLowerCase().includes(query) ||
          event.channel?.toLowerCase().includes(query) ||
          JSON.stringify(event.data).toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [events, selectedTypes, searchQuery]);

  const getEventTypeClasses = (type: CentrifugoEvent['type']) => {
    const typeMap: Record<
      CentrifugoEvent['type'],
      { badge: string; icon: string; text: string }
    > = {
      connected: {
        badge: 'bg-green-100 dark:bg-green-950/50 text-green-700 dark:text-green-300 border-green-300 dark:border-green-800',
        icon: '🟢',
        text: 'text-green-700 dark:text-green-300',
      },
      disconnected: {
        badge: 'bg-red-100 dark:bg-red-950/50 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800',
        icon: '🔴',
        text: 'text-red-700 dark:text-red-300',
      },
      subscribed: {
        badge: 'bg-blue-100 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-800',
        icon: '📡',
        text: 'text-blue-700 dark:text-blue-300',
      },
      unsubscribed: {
        badge: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700',
        icon: '📴',
        text: 'text-gray-700 dark:text-gray-300',
      },
      publication: {
        badge: 'bg-purple-100 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-800',
        icon: '📩',
        text: 'text-purple-700 dark:text-purple-300',
      },
      error: {
        badge: 'bg-red-100 dark:bg-red-950/50 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800',
        icon: '❌',
        text: 'text-red-700 dark:text-red-300',
      },
      info: {
        badge: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700',
        icon: 'ℹ️',
        text: 'text-gray-700 dark:text-gray-300',
      },
    };
    return typeMap[type];
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const handleExportLogs = () => {
    const logsText = filteredEvents
      .map(
        (e) =>
          `[${formatTime(e.timestamp)}] ${e.type.toUpperCase()}${e.channel ? ` [${e.channel}]` : ''}: ${e.message}`
      )
      .join('\n');

    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `centrifugo-logs-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleTypeToggle = (types: string[]) => {
    setSelectedTypes(types as CentrifugoEvent['type'][]);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-500" />
            <CardTitle>Live Event Log</CardTitle>
            <Badge variant="outline">{events.length} total</Badge>
            {filteredEvents.length !== events.length && (
              <Badge variant="outline" className="bg-blue-50 dark:bg-blue-950/20 text-blue-700 dark:text-blue-300">
                {filteredEvents.length} filtered
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            {events.length > 0 && (
              <>
                <Button variant="outline" size="sm" onClick={handleExportLogs}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline" size="sm" onClick={clearEvents}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Type Filters + Auto-scroll */}
          <div className="flex items-center justify-between gap-4">
            <ToggleGroup type="multiple" value={selectedTypes} onValueChange={handleTypeToggle} className="flex-wrap justify-start">
              <ToggleGroupItem value="error" size="sm" className="text-xs">
                ❌ Error
              </ToggleGroupItem>
              <ToggleGroupItem value="publication" size="sm" className="text-xs">
                📩 Pub
              </ToggleGroupItem>
              <ToggleGroupItem value="connected" size="sm" className="text-xs">
                🟢 Conn
              </ToggleGroupItem>
              <ToggleGroupItem value="disconnected" size="sm" className="text-xs">
                🔴 Disc
              </ToggleGroupItem>
              <ToggleGroupItem value="subscribed" size="sm" className="text-xs">
                📡 Sub
              </ToggleGroupItem>
              <ToggleGroupItem value="unsubscribed" size="sm" className="text-xs">
                📴 Unsub
              </ToggleGroupItem>
              <ToggleGroupItem value="info" size="sm" className="text-xs">
                ℹ️ Info
              </ToggleGroupItem>
            </ToggleGroup>

            <div className="flex items-center gap-2 flex-shrink-0">
              <Switch id="auto-scroll" checked={autoScroll} onCheckedChange={setAutoScroll} />
              <label htmlFor="auto-scroll" className="text-sm text-muted-foreground whitespace-nowrap cursor-pointer">
                Auto-scroll
              </label>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border border-border bg-muted/20 p-4" ref={scrollRef}>
          {filteredEvents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Activity className="h-12 w-12 mb-2 opacity-20" />
              <p className="text-sm">
                {events.length === 0
                  ? 'No events yet. Connect to Centrifugo to see real-time events.'
                  : 'No events match your filters.'}
              </p>
            </div>
          ) : (
            <div className="space-y-2 font-mono text-xs">
              {filteredEvents.map((event) => {
                const classes = getEventTypeClasses(event.type);
                return (
                  <div
                    key={event.id}
                    className="flex items-start gap-2 p-2 rounded bg-background/50 border border-border hover:bg-background/80 transition-colors"
                  >
                    <span className="text-base flex-shrink-0">{classes.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-muted-foreground flex-shrink-0">{formatTime(event.timestamp)}</span>
                        <Badge variant="outline" className={`${classes.badge} text-xs flex-shrink-0`}>
                          {event.type}
                        </Badge>
                        {event.channel && (
                          <Badge variant="outline" className="text-xs flex-shrink-0">
                            {event.channel}
                          </Badge>
                        )}
                      </div>
                      <p className={`${classes.text} break-words`}>{event.message}</p>
                      {event.data && (
                        <details className="mt-1">
                          <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                            View data
                          </summary>
                          <pre className="mt-1 p-2 bg-muted rounded text-[10px] overflow-x-auto">
                            {JSON.stringify(event.data, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
