'use client';

import { useEffect } from 'react';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from '@djangocfg/ui-core';

import { useRealtimeClient } from '../react/context';
import { useRealtimeState } from '../react/use-realtime-state';
import { FramesList } from './FramesList';
import { TopicsTable } from './TopicsTable';
import { connectionFacts, frameRows, phaseTone, topicRows } from './view-model';

import type { RealtimeSnapshot } from '../store';

export interface RealtimePanelProps {
  /** Accepted so the panel mounts as a `@djangocfg/devtools` custom tab. */
  isActive?: boolean;
  className?: string;
}

const selectAll = (s: RealtimeSnapshot) => s;

/** Connection state, topics with their offsets, and the last frames of the app's realtime client. */
export function RealtimePanel({ className }: RealtimePanelProps) {
  const client = useRealtimeClient();
  const snapshot = useRealtimeState(selectAll);
  // The frame log is kept only while a panel shows it.
  useEffect(() => client?.store.retainFrames(), [client]);
  const { connection } = snapshot;

  if (client === null) {
    return (
      <Empty className={className}>
        <EmptyHeader>
          <EmptyTitle>Realtime is off</EmptyTitle>
          <EmptyDescription>No realtime provider is mounted in this app.</EmptyDescription>
        </EmptyHeader>
      </Empty>
    );
  }

  const facts = connectionFacts(connection, Date.now());
  const factRows = facts.map((fact) => (
    <div key={fact.label} className="flex justify-between gap-4 text-sm">
      <dt className="text-muted-foreground">{fact.label}</dt>
      <dd className="font-mono text-xs">{fact.value}</dd>
    </div>
  ));
  const topics = topicRows(snapshot.topics);
  const frames = frameRows(snapshot.frames);
  const retry = connection.phase === 'reconnecting' && (
    <Button size="sm" variant="outline" onClick={client.retryNow}>
      Retry now
    </Button>
  );
  const topicsBody =
    topics.length === 0 ? <p className="text-sm text-muted-foreground">No topics subscribed.</p> : <TopicsTable rows={topics} />;
  const framesBody =
    frames.length === 0 ? <p className="text-sm text-muted-foreground">No frames yet.</p> : <FramesList rows={frames} />;

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <CardTitle className="flex items-center gap-2 text-base">
          Realtime <Badge variant={phaseTone(connection.phase)}>{connection.phase}</Badge>
        </CardTitle>
        {retry}
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <dl className="flex flex-col gap-1">{factRows}</dl>
        <section aria-label="Topics" className="flex flex-col gap-2">
          <h3 className="text-sm font-medium">Topics</h3>
          {topicsBody}
        </section>
        <section aria-label="Frames" className="flex flex-col gap-2">
          <h3 className="text-sm font-medium">Last frames</h3>
          {framesBody}
        </section>
      </CardContent>
    </Card>
  );
}
