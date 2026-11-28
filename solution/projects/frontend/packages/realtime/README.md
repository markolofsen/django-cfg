# @djangocfg/realtime

The browser half of django-cfg realtime: one WebSocket per tab, opened lazily,
reference-counted topics, replay after a reconnect and a refetch when history
no longer reaches the last offset. Protocol v1 is defined by django-cfg's
`django_realtime` module; this package mirrors it.

| Import | Holds |
|---|---|
| `@djangocfg/realtime` | `createRealtimeClient`, the protocol types and close codes, the store. No React, no DOM |
| `@djangocfg/realtime` (also) | `watchTopics` (refetch-style watching), `RealtimeTopic<E>` (the generated builders' shape) |
| `@djangocfg/realtime/react` | `RealtimeProvider`, `RealtimeClientProvider`, `useTopic`, `useRealtimeState`, `useRealtimeClient` |
| `@djangocfg/realtime/debug` | `RealtimePanel` (ui-core) |
| `@djangocfg/realtime/testing` | `createMockServer()`: protocol v1 in memory, for tests and stories |
| `@djangocfg/realtime/styles` | `@source` for the panel's classes: `@import` it after `ui-core/styles/full` |

## Usage

`BaseApp` from `@djangocfg/layouts` already mounts the provider inside its QueryClient and `AuthProvider`
(`realtime={false}` removes it). There are two ways to use a topic.

**A REST read that refreshes itself.** Mark the backend view `@invalidated_by("orders:{order_id}")` and run
`make gen`. The generated query carries the topic in `meta.realtimeTopics`, and `BaseApp` keeps the topic
subscribed while the query is mounted and invalidates it on each publication and on a gap, at most once per
~250 ms. The component is a plain generated hook, with no realtime code (the demo's `/realtime` page):

```tsx
import { useRealtimeDemoPingsList } from '@/api/generated/endpoints/realtime-demo/realtime-demo';

export function Pings() {
  const pings = useRealtimeDemoPingsList({ page_size: 10 }); // tagged `demo.pings`
  return <span>{pings.data?.count ?? 0}</span>;
}
```

**Events.** `useTopic` subscribes while the component is mounted and hands each event to a callback:

```tsx
'use client';
import { useState } from 'react';
import { useTopic } from '@djangocfg/realtime/react';
import { demoPingTopic } from '@/api/generated/realtime';

export function LastPing() {
  const [note, setNote] = useState('');
  useTopic(demoPingTopic(), (event) => setNote(event.note ?? ''));
  return <span>{note}</span>;
}
```

- **Typed topics.** `useTopic(ordersTopic({ orderId }), (event) => …)` takes a builder from the
  generated `realtime.ts`: `event` is typed by the topic's event model, and in development every
  payload is checked against its zod schema (a mismatch is logged and not delivered). The package
  never imports generated code; `RealtimeTopic<E>` is structural.
- **Cache refresh is the layout's job.** This package knows no cache. `@djangocfg/layouts` bridges
  React Query's QueryCache to the client with `watchTopics`: a topic is subscribed while a query with
  observers carries it in `meta.realtimeTopics`. Only a name containing `:` or `.` counts as a tag.
  There are no SWR keys and no key helpers (`useTopicRefresh`, `isKeyForTopic` and `topicsInKey` were
  removed).
- `useTopic(topic | null, onEvent, { onGap?, onRefused? })` returns the topic's `TopicState`
  (`pending`, `live`, `refused`, `leaving`, plus `offset`). Handlers may change identity; only a
  new topic resubscribes. `null` subscribes to nothing.
- `useRealtimeState()` returns the connection (`idle`, `connecting`, `live`, `reconnecting`,
  `stopped`); `useRealtimeState(s => s.topics[t])` selects a slice. A selector must return a
  value already in the snapshot, never a new object.
- **Gap → refetch.** On `sub_ok{recovered:false}` the topic's `onGap` runs, jittered 0–2 s. The
  server may send it again on a live subscription (a new epoch, or the bus trimmed past its reader):
  that is a gap too, and its offset is adopted. Without one, the provider's `onGap` runs; under
  `BaseApp` it invalidates the React Query queries tagged with the topic. A reconnect alone is
  never a gap. The message that follows a gap may carry the offset the gap announced; it is delivered.
- **First `sub_ok`.** `watchTopics` calls back once when a fresh subscription (one sent without
  `since`) is confirmed, so whatever was published between the REST read and the subscription is
  not missed. A resubscribe with `since` replays instead.

## Behaviour

- **Lazy.** No socket until the first subscription; closed 30 s after the last one leaves. A
  topic is unsubscribed 1.5 s after its last subscriber, so a StrictMode remount or a route
  change costs nothing.
- **Reconnect.** Full-jitter backoff, from the first retry: a random wait under 1 s, 2 s, 4 s …
  up to 30 s. The attempt counter resets only after a connection has been live for 10 s, so a
  server that accepts and drops at once still backs off. At once on `online` or when the page
  becomes visible. After 1011, 1012 or 1013 (keepalive, restart, slow consumer) the first retry
  waits a random 0–5 s. 4429 (too many connections) retries after 30 s plus jitter. Topics
  resubscribe with `since` = their last offset.
- **Keepalive.** A `ping` every `hello.ping` seconds; no `pong` within 10 s means the path is
  dead and the client reconnects.
- **Auth.** The cookie goes with the handshake; the first frame is always `auth`, with the token
  from `useAuth().getToken()` when there is one. Login or logout reconnects with the new identity. 4419 refreshes the
  token and reconnects at once (stopped if no session is left). Only 4401 and 4403 stop, until
  the auth state changes. `sub_err` is not retried, except `timeout`.
- **Echo.** `client.getCid()` is the live connection's id, for an `X-Realtime-Cid` request
  header; `meta.originCid` on an event names the connection whose request caused it.

## Issues

`onIssue(issue)` (client option, or `RealtimeProvider`/`BaseApp` `realtime.onIssue`) receives what a
person has to fix, never normal weather. Each issue carries `cid` (the live connection's id or
`null`) and never a token. Without a sink the client calls `console.warn`; `BaseApp` sends every
issue to `@djangocfg/devtools` and then to your `onIssue`.

| `kind` | When |
|---|---|
| `closed` | 4401, 4403, 4500, or a stop the client decided (code 0: no WebSocket, a bad URL, another protocol version) |
| `unreachable` | 5 attempts in a row ended without `hello`; once per streak |
| `refused` | `sub_err` `forbidden`, `invalid` or `unknown_topic` (with `topic`) |
| `protocol` | an `error` frame, or a frame the client could not parse |
| `invalid_event` | a typed topic's event failed its schema (development only) |

Never reported: 1006, 1011, 1012, 1013 or 4408 drops, a 4419 refresh, `sub_err` `limit`/`timeout`.

## Outside React

```ts
import { createRealtimeClient } from '@djangocfg/realtime';

const client = createRealtimeClient({ url: 'wss://api.example.com/ws', getToken });
const release = client.subscribe('demo.ping', (data, meta) => console.log(meta.offset, data));
```

## Debug panel

`<RealtimePanel />` shows the connection, every topic with its offset, and the last 50 frames
(an `auth` token is redacted). Frames are recorded only while a panel is mounted
(`store.retainFrames()`, reference-counted), so an app without one keeps no frame log. It
accepts `isActive`, so it mounts as a `@djangocfg/devtools` custom tab.

## Tests and stories

```ts
import { createMockServer } from '@djangocfg/realtime/testing';

const server = createMockServer();
const client = createRealtimeClient({ url: server.url, WebSocket: server.WebSocket });
server.publish('orders:42', { status: 'paid' });
server.drop();                    // network loss → backoff, replay with since
server.trim('orders:42', 1);      // history no longer reaches since → recovered:false
server.bumpEpoch('orders:42');    // history lost → recovered:false
server.closeAll(4401);            // close codes
server.sendRaw('{"op":"error"}'); // any frame, as the server would send it
```

Stories: `Packages/Realtime` (Live feed, Reconnect and replay, Gap refetch) run on the mock server.
