import type { StoredConversation, StoredMessage } from '../../wire/stored';

/** What the server says about the run the client lost track of. */
export type Reconciled =
  | { outcome: 'done' | 'error' | 'cancelled'; conversation: StoredConversation }
  /** The server never stored an answer: nothing ran, a resend with the same `client_id` is safe. */
  | { outcome: 'lost'; conversation: StoredConversation }
  /** Still running after the budget: offer Retry, keep looking on the next load. */
  | { outcome: 'timeout'; conversation: StoredConversation };

export interface ReconcileDeps {
  fetchConversation: (signal: AbortSignal) => Promise<StoredConversation>;
  signal: AbortSignal;
  sleep?: (ms: number, signal: AbortSignal) => Promise<void>;
  now?: () => number;
  pollMs?: number;
  budgetMs?: number;
}

const wait = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve) => {
    const timer = setTimeout(resolve, ms);
    signal.addEventListener('abort', () => {
      clearTimeout(timer);
      resolve();
    }, { once: true });
  });

const lastAssistant = (messages: StoredMessage[]): StoredMessage | undefined => [...messages].reverse().find((m) => m.role === 'assistant');

/**
 * Refetch the thread and trust the last assistant message (CONTRACT.md "Abort, loss and reconcile"): `done`, `error` and `cancelled` are final;
 * `running` is polled every 2 s for about 60 s. No replay, no resume: the stored message is the truth. A fetch failure throws; the caller shows Retry.
 */
export async function reconcile({ fetchConversation, signal, sleep = wait, now = Date.now, pollMs = 2000, budgetMs = 60_000 }: ReconcileDeps): Promise<Reconciled> {
  const deadline = now() + budgetMs;
  for (;;) {
    const conversation = await fetchConversation(signal);
    const last = lastAssistant(conversation.messages);
    if (!last) return { outcome: 'lost', conversation };
    if (last.status !== 'running') return { outcome: last.status, conversation };
    if (now() + pollMs > deadline || signal.aborted) return { outcome: 'timeout', conversation };
    await sleep(pollMs, signal);
  }
}
