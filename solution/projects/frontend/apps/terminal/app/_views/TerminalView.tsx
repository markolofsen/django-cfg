'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Empty,
  EmptyHeader,
  EmptyTitle,
  EmptyDescription,
  EmptyMedia,
} from '@djangocfg/ui-nextjs';
import { RefreshCw, Terminal, History } from 'lucide-react';
import { useTerminal } from '@lib/contexts';
import {
  SessionStats,
  SessionCard,
  CommandHistoryCard,
} from '@components';

export function TerminalView() {
  const {
    sessions,
    sessionsLoading,
    activeSessions,
    activeSessionsLoading,
    commands,
    commandsLoading,
    refreshSessions,
    refreshActiveSessions,
    refreshCommands,
    closeSession,
  } = useTerminal();

  const isLoading = sessionsLoading || activeSessionsLoading || commandsLoading;

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-muted rounded" />
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const handleRefresh = () => {
    refreshSessions();
    refreshActiveSessions();
    refreshCommands();
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Terminal</h1>
          <p className="text-muted-foreground mt-2">
            Manage terminal sessions and command history
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <SessionStats sessions={sessions} activeSessions={activeSessions} />

      {/* Tabs */}
      <Tabs defaultValue="active" className="space-y-6">
        <TabsList>
          <TabsTrigger value="active">Active Sessions</TabsTrigger>
          <TabsTrigger value="all">All Sessions</TabsTrigger>
          <TabsTrigger value="history">Command History</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Terminal Sessions</CardTitle>
              <CardDescription>Currently running terminal sessions</CardDescription>
            </CardHeader>
            <CardContent>
              {activeSessions.length === 0 ? (
                <Empty>
                  <EmptyHeader>
                    <EmptyMedia variant="icon">
                      <Terminal className="size-6" />
                    </EmptyMedia>
                    <EmptyTitle>No active sessions</EmptyTitle>
                    <EmptyDescription>
                      Terminal sessions are created via Electron app
                    </EmptyDescription>
                  </EmptyHeader>
                </Empty>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {activeSessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      onClose={closeSession}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="all" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Terminal Sessions</CardTitle>
              <CardDescription>Complete session history</CardDescription>
            </CardHeader>
            <CardContent>
              {sessions.length === 0 ? (
                <Empty>
                  <EmptyHeader>
                    <EmptyMedia variant="icon">
                      <Terminal className="size-6" />
                    </EmptyMedia>
                    <EmptyTitle>No sessions yet</EmptyTitle>
                    <EmptyDescription>
                      Sessions will appear here after creation
                    </EmptyDescription>
                  </EmptyHeader>
                </Empty>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {sessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      onClose={session.is_alive ? closeSession : undefined}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Command History</CardTitle>
              <CardDescription>Recently executed commands</CardDescription>
            </CardHeader>
            <CardContent>
              {commands.length === 0 ? (
                <Empty>
                  <EmptyHeader>
                    <EmptyMedia variant="icon">
                      <History className="size-6" />
                    </EmptyMedia>
                    <EmptyTitle>No command history</EmptyTitle>
                    <EmptyDescription>
                      Commands will appear here after execution
                    </EmptyDescription>
                  </EmptyHeader>
                </Empty>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {commands.map((command) => (
                    <CommandHistoryCard key={command.id} command={command} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
