import type { SessionStorage, ThreadApi } from '../../session';
import { scriptedTransport } from '../../session';
import type { StoredMessage, StoredThread } from '../../wire';
import { ThreadNotFoundError, type ChatTransport } from '../../wire';
import { DEMO_THREAD, demoReply, scriptText } from './thread';

interface Row {
  title: string;
  at: string;
  messages: StoredMessage[];
}

const OLD_TITLES = ['Quarterly report outline', 'Translate the pricing page', 'Draft a reply to the supplier', 'Why did signups drop in March?', 'Plan for the offsite', 'Summarise the support backlog'];

const stored = (over: Partial<StoredMessage>): StoredMessage => ({ id: 'm', seq: 1, role: 'user', text: '', parts: [], status: 'done', error_code: null, created_at: '2026-10-24T10:00:00Z', ...over });

/**
 * The demo's in-memory server: the long weekly thread, a dozen older chats (so the history screen has groups and a search), and a transport that answers by keyword (`demoReply`) and stores
 * what it said, so switching away and back shows the same conversation. `empty` starts with no open chat.
 */
export function createDemoServer({ empty = false }: { empty?: boolean } = {}) {
  const at = (hours: number) => new Date(Date.now() - hours * 3_600_000).toISOString();
  const db = new Map<string, Row>();
  if (!empty) db.set('demo', { title: 'Weekly overview', at: at(1), messages: DEMO_THREAD.messages });
  db.set('s-onboard', { title: 'How do we onboard a new client?', at: at(30), messages: [stored({ id: 'o1', text: 'How do we onboard a new client?' }), stored({ id: 'o2', seq: 2, role: 'assistant', text: 'Follow the onboarding checklist.' })] });
  db.set('s-holiday', { title: 'Where is the holiday calendar and who approves days off in the second half of the year?', at: at(24 * 9), messages: [stored({ id: 'h1', text: 'Where is the holiday calendar?' })] });
  for (let i = 0; i < 12; i += 1) db.set(`s-old-${i}`, { title: OLD_TITLES[i % OLD_TITLES.length]!, at: at(24 * (3 + i * 9)), messages: [stored({ id: `p${i}`, text: OLD_TITLES[i % OLD_TITLES.length]! })] });

  let serial = 0;
  const row = (id: string): StoredThread => {
    const t = db.get(id)!;
    return { id, title: t.title, last_message_at: t.at, message_count: t.messages.length };
  };
  const api: ThreadApi = {
    list: async () => [...db.keys()].map(row).sort((a, b) => b.last_message_at.localeCompare(a.last_message_at)),
    create: async () => {
      const id = `s-new-${++serial}`;
      db.set(id, { title: '', at: new Date().toISOString(), messages: [] });
      return row(id);
    },
    load: async (id) => {
      if (!db.has(id)) throw new ThreadNotFoundError();
      return { id, messages: db.get(id)!.messages };
    },
  };
  const transport: ChatTransport = {
    async *open(input) {
      const steps = demoReply(input.text, input.attachments?.length ?? 0);
      // Stored when the run starts: the adapter stops reading at the terminal frame, so nothing after the last `yield` is certain to run.
      const t = db.get(input.threadId ?? '');
      if (t) {
        t.title ||= input.text.slice(0, 80);
        t.at = new Date().toISOString();
        t.messages.push(stored({ id: `u${t.messages.length}`, seq: t.messages.length + 1, text: input.text }), stored({ id: `a${t.messages.length}`, seq: t.messages.length + 2, role: 'assistant', text: scriptText(steps) }));
      }
      yield* scriptedTransport(steps).open(input);
    },
  };
  let last: string | null = empty ? null : 'demo';
  const storage: SessionStorage = { read: () => last, write: (id) => void (last = id) };
  return { api, transport, storage };
}
