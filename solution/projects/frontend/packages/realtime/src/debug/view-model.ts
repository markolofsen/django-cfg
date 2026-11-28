import type { ConnectionPhase, ConnectionState, FrameRecord, TopicState, TopicStatus } from '../store';

export type BadgeTone = 'default' | 'secondary' | 'destructive' | 'outline';

const PHASE_TONE: Record<ConnectionPhase, BadgeTone> = {
  idle: 'outline',
  connecting: 'secondary',
  live: 'default',
  reconnecting: 'secondary',
  stopped: 'destructive',
};

const STATUS_TONE: Record<TopicStatus, BadgeTone> = {
  pending: 'secondary',
  live: 'default',
  refused: 'destructive',
  leaving: 'outline',
};

export interface Fact {
  label: string;
  value: string;
}

export interface TopicRow {
  topic: string;
  status: TopicStatus;
  tone: BadgeTone;
  offset: string;
  subscribers: number;
  received: number;
  gaps: number;
  note: string;
}

export interface FrameRow {
  id: number;
  time: string;
  direction: string;
  op: string;
  topic: string;
  text: string;
}

const DASH = '—';

export function phaseTone(phase: ConnectionPhase): BadgeTone {
  return PHASE_TONE[phase];
}

export function connectionFacts(connection: ConnectionState, now: number): Fact[] {
  const retry =
    connection.retryAt === null ? DASH : `in ${Math.max(0, Math.round((connection.retryAt - now) / 100) / 10)} s`;
  const close = connection.lastClose;
  return [
    { label: 'User', value: connection.user === null ? 'anonymous' : String(connection.user) },
    { label: 'Connection id', value: connection.cid ?? DASH },
    { label: 'Attempt', value: String(connection.attempt) },
    { label: 'Next retry', value: retry },
    { label: 'Last close', value: close === null ? DASH : `${close.code}${close.reason ? ` ${close.reason}` : ''}` },
  ];
}

export function topicRows(topics: Readonly<Record<string, TopicState>>): TopicRow[] {
  return Object.entries(topics)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([topic, state]) => ({
      topic,
      status: state.status,
      tone: STATUS_TONE[state.status],
      offset: state.offset ?? DASH,
      subscribers: state.subscribers,
      received: state.received,
      gaps: state.gaps,
      note: state.refusal ?? '',
    }));
}

function clockTime(at: number): string {
  return new Date(at).toISOString().slice(11, 23);
}

/** Newest first. */
export function frameRows(frames: readonly FrameRecord[]): FrameRow[] {
  return [...frames].reverse().map((frame) => ({
    id: frame.id,
    time: clockTime(frame.at),
    direction: frame.direction === 'in' ? '↓' : '↑',
    op: frame.op,
    topic: frame.topic ?? '',
    text: frame.text,
  }));
}
