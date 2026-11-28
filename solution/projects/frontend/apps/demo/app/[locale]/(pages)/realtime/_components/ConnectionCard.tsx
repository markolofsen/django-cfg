'use client';

import { Badge, Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-core';
import { useRealtimeState } from '@djangocfg/realtime/react';

import { useAppTranslations } from '@i18n';

import type { ConnectionPhase } from '@djangocfg/realtime';

const PHASE_VARIANT: Record<ConnectionPhase, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  idle: 'outline',
  connecting: 'secondary',
  live: 'default',
  reconnecting: 'secondary',
  stopped: 'destructive',
};

/** `useRealtimeState()`: the tab's one socket. */
export function ConnectionCard() {
  const { app } = useAppTranslations();
  const connection = useRealtimeState();
  const user = connection.user === null ? app('realtime.anonymous') : String(connection.user);
  const cid = connection.cid ?? '—';

  return (
    <Card>
      <CardHeader>
        <CardTitle>{app('realtime.connection')}</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">{app('realtime.phase')}</dt>
            <dd>
              <Badge variant={PHASE_VARIANT[connection.phase]}>{connection.phase}</Badge>
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">{app('realtime.cid')}</dt>
            <dd className="font-mono text-xs">{cid}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">{app('realtime.user')}</dt>
            <dd className="font-mono text-xs">{user}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
