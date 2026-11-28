import type { StoredConversation, StoredThread } from '../../wire/stored';
import { ThreadNotFoundError } from '../../wire/transport';

/** The session endpoints (`/apix/chat/v1/threads`), supplied by the app. `load` throws `ThreadNotFoundError` for a session that is not the viewer's or is gone. */
export interface ThreadApi {
  /** The viewer's sessions with messages, newest activity first. */
  list: (signal: AbortSignal) => Promise<StoredThread[]>;
  /** A new, empty session (`POST threads`). */
  create: () => Promise<StoredThread>;
  /** One session with its last messages. */
  load: (id: string, signal: AbortSignal) => Promise<StoredConversation>;
}

/** Where the last used session id is kept (the host picks the key). Reads and writes must never throw. */
export interface SessionStorage {
  read: () => string | null;
  write: (id: string | null) => void;
}

export const NO_SESSION: StoredConversation = { id: null, messages: [] };

/**
 * The session to show on page load: the remembered one, else the newest, else none (a session is created on the first send, never on load).
 * A remembered id that is gone (another account on this browser, a purged session) is forgotten and the newest takes over.
 */
export async function restoreSession({ api, storage, signal }: { api: ThreadApi; storage?: SessionStorage; signal: AbortSignal }): Promise<StoredConversation> {
  const remembered = storage?.read() ?? null;
  if (remembered) {
    try {
      return await api.load(remembered, signal);
    } catch (error) {
      if (!(error instanceof ThreadNotFoundError)) throw error;
      storage?.write(null);
    }
  }
  const [newest] = await api.list(signal);
  return newest ? api.load(newest.id, signal) : NO_SESSION;
}

const STEPS: ReadonlyArray<[Intl.RelativeTimeFormatUnit, number]> = [
  ['year', 31_536_000],
  ['month', 2_592_000],
  ['week', 604_800],
  ['day', 86_400],
  ['hour', 3_600],
  ['minute', 60],
];

/** "5 minutes ago" in the viewer's language; under a minute it is `now` (the unit `numeric: 'auto'` words as "now"). */
export function relativeTime(iso: string, locale: string, now: number = Date.now()): string {
  const seconds = Math.round((Date.parse(iso) - now) / 1000);
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  const abs = Math.abs(seconds);
  for (const [unit, size] of STEPS) {
    if (abs >= size) return formatter.format(Math.round(seconds / size), unit);
  }
  return formatter.format(0, 'second');
}
