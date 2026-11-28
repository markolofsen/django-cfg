import { isEmpty, type Draft } from "./outbound";

/**
 * Prompts written while the agent is working.
 *
 * ## Why this exists
 *
 * `store.send` opened with `if (state.inFlight !== null) return;` — a second
 * turn was DISCARDED, silently. Our agents run for minutes, so the moment a user
 * most often has something to add is exactly the moment the composer threw it
 * away. Nothing reported it: no error, no toast, the text simply vanished from
 * the field.
 *
 * ## Draft objects, never strings
 *
 * A queued entry is a whole `Draft`. A queue of strings would drop the picked
 * tools a turn carries beside its text. `core/compose/outbound` already owns what a
 * sendable turn is; this holds those.
 *
 * ## No settings
 *
 * Whether to queue is not a preference. Enter while streaming queues, always.
 * A toggle here would be a question with no good default, asked of someone who
 * is mid-sentence.
 */

export interface QueuedPrompt {
  readonly id: string;
  readonly draft: Draft;
}

export interface QueueState {
  readonly items: readonly QueuedPrompt[];
}

export const emptyQueue: QueueState = { items: [] };

/**
 * Append, unless the draft is empty.
 *
 * Empty is rejected here rather than at the call site so every entry point —
 * keyboard, button, a host calling directly — obeys one rule. Queueing nothing
 * would put a row in the strip that sends nothing when it drains.
 */
export function enqueue(state: QueueState, draft: Draft, id: string): QueueState {
  if (isEmpty(draft)) return state;
  return { items: [...state.items, { id, draft }] };
}

/**
 * Take the next prompt, or null.
 *
 * Returns the REMAINDER alongside it rather than mutating: the caller sends the
 * draft and stores the rest, so a send that throws cannot leave the queue in a
 * state where the prompt is both gone and unsent.
 */
export function dequeue(state: QueueState): {
  readonly next: QueuedPrompt | null;
  readonly rest: QueueState;
} {
  const [next, ...rest] = state.items;
  if (next === undefined) return { next: null, rest: state };
  return { next, rest: { items: rest } };
}

export function removeQueued(state: QueueState, id: string): QueueState {
  return { items: state.items.filter((item) => item.id !== id) };
}

/**
 * Move one prompt to the head, keeping the rest in order.
 *
 * "Send now" names a ROW, and the drain always takes the head — so without this
 * the button beside the third prompt would release the first. Promotion rather
 * than a send-this-one path because one code owner for "what goes next" is what
 * keeps the forced release and the natural one from drifting apart.
 *
 * An unknown id returns the state unchanged rather than throwing: the row can be
 * removed by another click between render and dispatch, and a queue that throws
 * on a stale id would take the composer down for a race the user cannot see.
 */
export function promoteQueued(state: QueueState, id: string): QueueState {
  const chosen = state.items.find((item) => item.id === id);
  if (chosen === undefined) return state;
  return { items: [chosen, ...state.items.filter((item) => item.id !== id)] };
}

/**
 * Replace a queued draft — the edit affordance.
 *
 * An edit to empty REMOVES the entry. The alternative is a row the user has
 * emptied on purpose that still occupies the strip and still sends nothing, and
 * "delete it yourself" is an extra action for something already expressed.
 */
export function editQueued(state: QueueState, id: string, draft: Draft): QueueState {
  if (isEmpty(draft)) return removeQueued(state, id);
  return {
    items: state.items.map((item) => (item.id === id ? { ...item, draft } : item)),
  };
}
