/** A stored message as the host's history endpoint returns it. The shape is the host's server's; this is the part the widget reads. */
export type StoredStatus = 'done' | 'running' | 'error' | 'cancelled';

import type { StoredTrace } from './trace';

/** A structured part the answer carried, by the same `kind` a live `ui_payload` has. */
export interface StoredPart {
  kind: string;
  data: unknown;
}

/** A file on a user message. `url` is short-lived: a reload fetches the thread again for a fresh one. */
export interface StoredAttachment {
  id: string;
  name: string;
  mime: string;
  size: number;
  kind: string;
  url: string;
  /** The server deleted the bytes after the kind's retention: `url` is empty and the chat shows a muted chip. */
  expired?: boolean;
}

export interface StoredMessage {
  id: string;
  seq: number;
  role: 'user' | 'assistant';
  text: string;
  parts: StoredPart[];
  /** Files of a user message; absent from a host whose server has none. */
  attachments?: StoredAttachment[];
  /** What the answer did (TraceStep v1), read at the kind's trace level. `null` or absent: nothing was recorded (a user message, a kind with tracing off, an older server). */
  trace?: StoredTrace | null;
  status: StoredStatus;
  error_code: string | null;
  created_at: string;
}

/** One session with its last messages; `id: null` is the state before the first send (no session exists yet, or the host is anonymous). */
export interface StoredConversation {
  id: string | null;
  messages: StoredMessage[];
}

/** A session in the list (`GET threads/`): `title` is the first user message, empty until its first answer finishes. */
export interface StoredThread {
  id: string;
  title: string;
  last_message_at: string;
  message_count: number;
}
