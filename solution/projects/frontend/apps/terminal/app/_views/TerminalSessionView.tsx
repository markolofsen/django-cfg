'use client';

import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  Button,
  Badge,
} from '@djangocfg/ui-nextjs';
import { ArrowLeft, Terminal, RotateCcw, Loader2 } from 'lucide-react';

import { useTerminalSessionsRetrieve } from '@lib/api/generated/terminal/_utils/hooks';
import { terminalClient } from '@lib/api/BaseClient';
import type { API } from '@lib/api/generated/terminal';
import { InteractiveTerminal } from '@components/InteractiveTerminal';
import { TerminalHeader } from '@components';

interface TerminalSessionViewProps {
  sessionId: string;
}

export function TerminalSessionView({ sessionId }: TerminalSessionViewProps) {
  const router = useRouter();
  const { data: session, error, isLoading, mutate } = useTerminalSessionsRetrieve(sessionId, terminalClient as unknown as API);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Session Not Found</h1>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-muted-foreground mb-4">
              Session {sessionId} does not exist or has been closed.
            </p>
            <Button onClick={() => router.push('/')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Sessions
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isConnected = session.status === 'connected';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Terminal className="w-6 h-6" />
          <h1 className="text-2xl font-bold">
            {session.display_name || session.name || 'Terminal Session'}
          </h1>
          <Badge variant={isConnected ? 'default' : 'secondary'}>
            {session.status}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => mutate()}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={() => router.push('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </div>
      </div>

      <p className="text-sm text-muted-foreground">
        Shell: {session.shell} | Directory: {session.working_directory}
      </p>

      {/* Session Info */}
      <TerminalHeader session={session} />

      {/* Terminal */}
      <Card className="min-h-[500px] overflow-hidden bg-black">
        <InteractiveTerminal
          sessionId={sessionId}
          isActive={isConnected}
        />
      </Card>
    </div>
  );
}
