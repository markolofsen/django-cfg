/**
 * The prompt ladder: what ArrowUp and ArrowDown land on, as pure state.
 *
 * `boundary.ts` answers "may this press navigate"; this answers "to what". Split
 * because they fail differently — a boundary bug moves the caret when it should
 * not, a ladder bug loses the user's draft — and because the boundary rules were
 * ported verbatim while this is where the queue rung is new.
 *
 * ## The ladder, from the bottom
 *
 *   draft            ← what the user was typing, stashed on the first ArrowUp
 *   queued (last)    ← the newest prompt waiting to be sent, if any
 *   sent[n-1]        ← the most recent sent prompt
 *   …
 *   sent[0]          ← the oldest kept
 *
 * ArrowUp climbs, ArrowDown descends, and the bottom is always the draft the
 * user had before they started walking. Losing that draft is the failure this
 * design exists to prevent: a user presses Up once out of curiosity and their
 * half-written message must come back on Down.
 *
 * ## Why the queue is a rung, and only its LAST entry
 *
 * A queued prompt was written but not answered, so it is the nearest thing in
 * time to the draft — closer than anything already sent. Only the last one is a
 * rung: it is the one a user reaching backwards means, and it is the one they
 * would edit. Walking the whole queue would put entries the user can already
 * see, and remove, into a ladder they cannot see.
 *
 * ## Why `index` is not enough on its own
 *
 * The pending rung cannot be an index into `sent` — it sits between the draft
 * and `sent[n-1]` and belongs to neither array. Encoding it as `index === -1`
 * would make it indistinguishable from "not walking at all", and a second
 * ArrowDown would then jump to the draft, skipping every entry just walked.
 * Hence an explicit position type.
 */

/** Where the ladder currently is. `draft` is the bottom and the resting state. */
export type RecallPosition =
  | { readonly kind: "draft" }
  | { readonly kind: "queued" }
  | { readonly kind: "sent"; readonly index: number };

export interface RecallState {
  readonly position: RecallPosition;
  /**
   * The user's own text, held while they walk.
   *
   * `null` means nothing is stashed — i.e. the ladder is at rest. Stashed ONCE,
   * on the first step off the draft, never on subsequent steps: re-stashing
   * would overwrite the user's text with a recalled entry and the draft would be
   * gone with no way back.
   */
  readonly stashedDraft: string | null;
  /**
   * What recall last wrote into the buffer.
   *
   * `bufferIsRecallOwned` reads this to tell "the user typed this" from "recall
   * put this here". Cleared when the ladder returns to rest, so a stale value
   * cannot make a fresh draft look recall-owned.
   */
  readonly lastRecalled: string | null;
}

export interface RecallLadder {
  /** Sent prompts, OLDEST first — the order ArrowUp walks backwards through. */
  readonly sent: readonly string[];
  /** Prompts queued behind an in-flight turn, oldest first. Only the last is a rung. */
  readonly queued: readonly string[];
}

/** A move's outcome: the new state, and the text to put in the buffer. */
export interface RecallMove {
  readonly state: RecallState;
  /** `null` ⇒ nothing moved; the caller must NOT write to the buffer. */
  readonly text: string | null;
}

export const REST: RecallState = {
  position: { kind: "draft" },
  stashedDraft: null,
  lastRecalled: null,
};

/** The queue rung exists only when the newest queued prompt has content. */
function queuedRung(ladder: RecallLadder): string | null {
  const last = ladder.queued[ladder.queued.length - 1];
  return last !== undefined && last !== "" ? last : null;
}

/**
 * Step UP one rung.
 *
 * `draft` is the current buffer, stashed on the first step so ArrowDown can
 * return it. Returns `text: null` when there is nowhere to go, which is how the
 * caller knows to leave the key to the textarea rather than swallowing it.
 */
export function recallPrevious(
  state: RecallState,
  ladder: RecallLadder,
  draft: string,
): RecallMove {
  // Stash before anything else, and only at rest: `stashedDraft` is the user's
  // text, and overwriting it mid-walk with a recalled entry loses it silently.
  const stashedDraft = state.position.kind === "draft" ? draft : state.stashedDraft;

  const step = (position: RecallPosition, text: string): RecallMove => ({
    state: { position, stashedDraft, lastRecalled: text },
    text,
  });

  if (state.position.kind === "draft") {
    const pending = queuedRung(ladder);
    if (pending !== null) return step({ kind: "queued" }, pending);
    const newest = ladder.sent.length - 1;
    if (newest < 0) return { state, text: null };
    return step({ kind: "sent", index: newest }, ladder.sent[newest] ?? "");
  }

  if (state.position.kind === "queued") {
    const newest = ladder.sent.length - 1;
    if (newest < 0) return { state, text: null };
    return step({ kind: "sent", index: newest }, ladder.sent[newest] ?? "");
  }

  const next = state.position.index - 1;
  // At the oldest entry: stay. Wrapping to the newest would make a long ladder
  // an infinite loop with no way to tell you had reached the end.
  if (next < 0) return { state, text: null };
  return step({ kind: "sent", index: next }, ladder.sent[next] ?? "");
}

/**
 * Step DOWN one rung, ending at the stashed draft.
 *
 * At rest this does nothing and returns `text: null` — ArrowDown in an untouched
 * composer belongs to the textarea.
 */
export function recallNext(state: RecallState, ladder: RecallLadder): RecallMove {
  if (state.position.kind === "draft") return { state, text: null };

  const land = (): RecallMove => {
    const text = state.stashedDraft ?? "";
    // Back at rest: `lastRecalled` is cleared with the same write, so the
    // restored draft is the USER's again and a further arrow will not navigate
    // unless the buffer is empty.
    return { state: REST, text };
  };

  if (state.position.kind === "queued") return land();

  const next = state.position.index + 1;
  if (next < ladder.sent.length) {
    const text = ladder.sent[next] ?? "";
    return {
      state: { ...state, position: { kind: "sent", index: next }, lastRecalled: text },
      text,
    };
  }

  // Past the newest sent entry: the queued rung, then the draft.
  const pending = queuedRung(ladder);
  if (pending !== null) {
    return {
      state: { ...state, position: { kind: "queued" }, lastRecalled: pending },
      text: pending,
    };
  }
  return land();
}
