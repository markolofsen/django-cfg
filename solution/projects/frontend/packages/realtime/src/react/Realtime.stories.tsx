import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-core';

import { createRealtimeClient } from '../client';
import { RealtimePanel } from '../debug';
import { createMockServer } from '../testing';
import { RealtimeClientProvider } from './context';
import { useTopic } from './use-topic';

import type { RealtimeClient } from '../client';
import type { MockServer } from '../testing';

const TOPIC = 'demo.ping';

interface FeedItem {
  offset: string;
  text: string;
}

/** One mock server and one client per story mount; nothing leaves the browser. */
function useMockRealtime(): { server: MockServer; client: RealtimeClient } {
  const [pair] = React.useState(() => {
    const server = createMockServer({ ping: 5 });
    const client = createRealtimeClient({ url: server.url, WebSocket: server.WebSocket });
    return { server, client };
  });
  return pair;
}

function useAutoPublish(server: MockServer, everyMs: number): void {
  React.useEffect(() => {
    let n = 0;
    const timer = setInterval(() => {
      n += 1;
      server.publish(TOPIC, { n, at: new Date().toISOString() });
    }, everyMs);
    return () => clearInterval(timer);
  }, [server, everyMs]);
}

function Feed({ refetches }: { refetches: number | null }) {
  const [items, setItems] = React.useState<FeedItem[]>([]);
  const onEvent = React.useCallback((data: unknown, meta: { offset: string }) => {
    setItems((prev) => [{ offset: meta.offset, text: JSON.stringify(data) }, ...prev].slice(0, 12));
  }, []);
  const state = useTopic(TOPIC, onEvent);
  const rows = items.map((item) => (
    <li key={item.offset} className="flex gap-3 font-mono text-xs">
      <span className="text-muted-foreground">{item.offset}</span>
      <span>{item.text}</span>
    </li>
  ));
  const refetchBadge = refetches !== null && <Badge variant="secondary">refetched {refetches}×</Badge>;
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-base">
          <code>{TOPIC}</code>
        </CardTitle>
        <div className="flex gap-2">
          {refetchBadge}
          <Badge variant="outline">{state?.status ?? 'none'}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-1">{rows}</ul>
      </CardContent>
    </Card>
  );
}

function Controls({ actions }: { actions: { label: string; run: () => void }[] }) {
  const buttons = actions.map((a) => (
    <Button key={a.label} size="sm" variant="outline" onClick={a.run}>
      {a.label}
    </Button>
  ));
  return <div className="flex flex-wrap gap-2">{buttons}</div>;
}

function Layout({ client, onGap, controls, refetches }: {
  client: RealtimeClient;
  onGap?: (topic: string) => void;
  controls: React.ReactNode;
  refetches: number | null;
}) {
  return (
    <RealtimeClientProvider client={client} onGap={onGap}>
      <div className="grid gap-4 p-4 lg:grid-cols-2">
        <div className="flex flex-col gap-4">
          {controls}
          <Feed refetches={refetches} />
        </div>
        <RealtimePanel />
      </div>
    </RealtimeClientProvider>
  );
}

function LiveFeedDemo() {
  const { server, client } = useMockRealtime();
  useAutoPublish(server, 2_000);
  const controls = <Controls actions={[{ label: 'Publish now', run: () => server.publish(TOPIC, { manual: true }) }]} />;
  return <Layout client={client} controls={controls} refetches={null} />;
}

function ReconnectDemo() {
  const { server, client } = useMockRealtime();
  useAutoPublish(server, 1_000);
  const controls = (
    <Controls
      actions={[
        { label: 'Drop the network', run: () => server.drop() },
        { label: 'Restart the server (1012)', run: () => server.restart() },
        { label: 'Refuse handshakes', run: () => { server.refuse(1006); server.drop(); } },
        { label: 'Accept handshakes', run: () => { server.refuse(null); client.retryNow(); } },
      ]}
    />
  );
  return <Layout client={client} controls={controls} refetches={null} />;
}

function GapDemo() {
  const { server, client } = useMockRealtime();
  const [refetches, setRefetches] = React.useState(0);
  useAutoPublish(server, 1_000);
  const onGap = React.useCallback(() => setRefetches((n) => n + 1), []);
  const loseHistory = () => {
    server.drop();
    server.bumpEpoch(TOPIC);
  };
  const outlive = () => {
    server.drop();
    for (let i = 0; i < 5; i += 1) server.publish(TOPIC, { missed: i });
    server.trim(TOPIC, 1);
  };
  const controls = (
    <Controls
      actions={[
        { label: 'Drop and trim history', run: outlive },
        { label: 'Drop and lose history (new epoch)', run: loseHistory },
        { label: 'Drop only (recovers)', run: () => server.drop() },
      ]}
    />
  );
  return <Layout client={client} onGap={onGap} controls={controls} refetches={refetches} />;
}

const meta: Meta = {
  title: 'Packages/Realtime',
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          '`@djangocfg/realtime` against the in-memory mock server from `@djangocfg/realtime/testing`: no backend needed.',
      },
    },
  },
};

export default meta;
type Story = StoryObj;

/** Messages arrive on one lazy socket; the panel shows the topic offset and the frames. */
export const LiveFeed: Story = { name: 'Live feed', render: () => <LiveFeedDemo /> };

/** Drop or restart the server: the client backs off, resubscribes with `since` and replays what it missed. */
export const ReconnectAndReplay: Story = { name: 'Reconnect and replay', render: () => <ReconnectDemo /> };

/** History that no longer reaches the last offset answers `recovered:false`; the app refetches (jittered 0–2 s). */
export const GapRefetch: Story = { name: 'Gap refetch', render: () => <GapDemo /> };
