import { useCallback, useRef, useState, type KeyboardEvent, type RefObject } from "react";

import {
  atFirstLine,
  atLastLine,
  bufferIsRecallOwned,
  recallNext,
  recallPrevious,
  REST,
  type RecallLadder,
  type RecallState,
} from "../../core/compose/recall";
import type { Draft } from "../../core/compose/outbound";
import { useChatEvents } from "../hooks";
import { useQueue } from "./use-queue";

/**
 * ↑/↓ prompt recall, bound to the textarea.
 *
 * Deliberately thin, the same split `useMentions` makes: every rule lives in
 * `core/compose/recall` where it is tested in milliseconds without a DOM, and this file
 * does three things a pure function cannot — read the caret out of the live
 * node, write the buffer, and claim the key.
 *
 * ## Why the state is a ref and not `useState`
 *
 * Nothing here RENDERS from the ladder position. The only visible effect of a
 * press is the text, which the composer store already owns, so state would buy a
 * re-render per keystroke and nothing else. It also has to be readable
 * synchronously inside the keydown handler: with `useState` the second of two
 * fast presses would read the first press's stale value and walk the same rung
 * twice.
 */

export interface UseRecallOptions {
  /** Sent prompts, OLDEST first. The host owns storage — see below. */
  readonly entries: readonly string[];
  /** The live textarea, for the caret. Recall is refused while it is null. */
  readonly input: RefObject<HTMLTextAreaElement | null>;
  /**
   * The composer's draft, passed in rather than read from its context.
   *
   * `store/` may not import `composer/` (`layers.test.ts`), and that boundary is
   * right here for a reason beyond the gate: recall needs the TEXT, not the
   * composer. Taking it as data keeps the hook usable by any surface that
   * holds a draft.
   */
  readonly draft: Draft;
  /** Writes the recalled entry into the buffer. */
  readonly setText: (value: string) => void;
}

export interface UseRecallResult {
  /**
   * Feed this to `ComposerInput.onKeyDown`.
   *
   * Calls `preventDefault()` only when it actually navigates, so an arrow that
   * should move the caret still does — that veto is the whole protocol.
   */
  readonly onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
  /**
   * The prompt Tab would insert, or `null` when the ladder is at rest.
   *
   * The one piece of recall that RENDERS, and therefore the one piece held as
   * state rather than in the ref below.
   */
  readonly preview: string | null;
  /** Drop the ladder back to rest. Call after a send. */
  readonly reset: () => void;
}

/**
 * Where the ladder COMES FROM is the host's, and the two sources are not
 * equivalent.
 *
 * A host may persist what was typed, or derive the ladder from the user turns
 * already in the transcript. Deriving is cheaper and
 * needs no storage, but it cannot recall a prompt that was sent and never
 * landed, and it is empty until history loads — so an empty ladder there is a
 * boundary, not a fault.
 *
 * Either way it stays off the wire: what you typed is a local editing
 * convenience, not conversation state, and must not sync between devices or
 * outlive the device it was typed on. This hook takes the ladder as data and
 * owns neither choice.
 */
export function useRecall({ entries, input, draft, setText }: UseRecallOptions): UseRecallResult {
  // Queued prompts are a rung of the same ladder: written but not answered, so
  // nearer in time than anything sent. Read from the store rather than taken as
  // an option — the queue is the package's own state and a host passing its own
  // copy would be a second source of truth for it.
  const { items, take } = useQueue();
  const events = useChatEvents();
  const state = useRef<RecallState>(REST);
  // The ONE thing recall renders. State, unlike the position beside it: a
  // preview that lived in a ref would move without repainting, which is the
  // whole feature.
  const [preview, setPreview] = useState<string | null>(null);
  // The same value, readable SYNCHRONOUSLY. The handler decides whether Tab is
  // recall's or the browser's, and a `useState` read there is one render stale
  // — so the first Tab after an arrow would fall through and move focus out of
  // the composer instead of inserting.
  const walking = useRef<string | null>(null);
  walking.current = preview;
  // Which queued entry the preview came from, or null when the rung is a sent
  // prompt. Read on Tab: a queued prompt is TAKEN and a sent one is copied, and
  // the text alone cannot tell them apart — the same words may sit on both rungs.
  const previewQueuedId = useRef<string | null>(null);

  // Read through refs so the handler identity is stable: it goes onto
  // `ComposerInput`, and a new function every render would defeat its
  // `useCallback` for no benefit.
  const latest = useRef({ entries, draft, items });
  latest.current = { entries, draft, items };

  /**
   * Typing abandons the walk.
   *
   * A preview left hanging while the user writes something new invites a Tab
   * that destroys it. Keyed on the draft becoming NON-EMPTY rather than on a
   * keystroke, because that is the condition — recall only walks on an empty
   * buffer, so any text at all means the user has started authoring.
   *
   * Derived during render rather than in an effect: an effect would paint one
   * frame with a stale preview over text that is already there.
   */
  if (preview !== null && draft.text !== "") {
    state.current = REST;
    walking.current = null;
    previewQueuedId.current = null;
    setPreview(null);
  }

  const reset = useCallback(() => {
    state.current = REST;
    previewQueuedId.current = null;
    setPreview(null);
  }, []);

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      // Another handler already claimed it — an open mention menu owns the
      // arrows while it is showing, and it renders over this same textarea.
      if (event.defaultPrevented) return;

      const node = input.current;

      // Tab and Escape belong to recall ONLY while a preview is showing.
      //
      // The Tab guard is an accessibility rule, not a preference: a Tab that is
      // always swallowed makes the composer a keyboard trap with no way out. So
      // both keys fall through untouched at rest, and Tab keeps moving focus.
      if (walking.current !== null) {
        if (event.key === "Tab") {
          event.preventDefault();
          const text = walking.current;
          const queuedId = previewQueuedId.current;
          state.current = REST;
          previewQueuedId.current = null;
          setPreview(null);
          // A queued prompt is TAKEN, a sent one copied. It has not been seen by
          // anyone, so leaving the entry behind would send it twice: once from
          // the queue and once as the edit the user is about to make. A sent
          // turn already happened, and rewriting it is a separate, destructive
          // operation that stays explicit.
          // Through `latest`, like every other queue read in this handler: the
          // callback is not re-created per keystroke, so a closed-over `items`
          // would be whatever the queue held when it was built.
          const taken =
            queuedId === null
              ? undefined
              : latest.current.items.find((item) => item.id === queuedId);
          if (queuedId !== null) take(queuedId);
          setText(text);
          // After BOTH steps, never between them. The queue's own edit path
          // orders them the other way round on purpose, so this must stay a
          // notification rather than the mechanism either path relies on.
          if (queuedId !== null && taken !== undefined) {
            events.emit("queue:taken", { id: queuedId, draft: taken.draft });
          }
          // Caret at the END: the user is about to edit or resend, and a caret
          // at 0 puts every keystroke in front of what they just inserted.
          // Deferred because React writes the value on the next commit.
          queueMicrotask(() => node?.setSelectionRange(text.length, text.length));
          return;
        }
        if (event.key === "Escape") {
          // Nothing to restore: the draft was never written to. That is the
          // point of the design — `stashedDraft` used to exist for this.
          //
          // The queued entry is left ALONE: Escape abandons the walk, and a
          // prompt the user only looked at must stay in the queue.
          event.preventDefault();
          event.stopPropagation();
          state.current = REST;
          previewQueuedId.current = null;
          setPreview(null);
          return;
        }
      }

      if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
      // A chord is the OS's or the host's: cmd+Up is "top of document" on macOS,
      // and shift+Up extends a selection.
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;

      if (node === null) return;

      const { entries: sent, draft: current, items: queued } = latest.current;
      const caret = { start: node.selectionStart, end: node.selectionEnd };

      // The cheapest and most absolute rule first: text the user typed is
      // theirs, and no caret position makes an arrow navigate away from it.
      //
      // `lastRecalled` is passed as `null` DELIBERATELY, and the argument is
      // now vestigial rather than merely unused: recall no longer writes to the
      // buffer, so whatever is in it is always the user's. The rule that
      // survives is the original half — a non-empty draft does not navigate —
      // and passing a remembered value could only ever weaken it.
      if (!bufferIsRecallOwned(current.text, null)) return;

      const ladder: RecallLadder = {
        sent,
        queued: queued.map((item) => item.draft.text),
      };
      const up = event.key === "ArrowUp";
      // The boundary decides whether this press is "move the caret within a
      // multi-line draft" or "leave the buffer" — zsh's rule, not "is the
      // composer empty".
      if (up ? !atFirstLine(current.text, caret) : !atLastLine(current.text, caret)) return;

      const move = up
        ? recallPrevious(state.current, ladder, current.text)
        : recallNext(state.current, ladder);

      // Nothing to move to: leave the key alone rather than swallowing it, so
      // ArrowUp in an empty composer with no history behaves like a textarea.
      if (move.text === null) return;

      event.preventDefault();
      state.current = move.state;
      // PREVIEW, never write. Walking must not touch the buffer: a full-buffer
      // rewrite per press reflows the composer, so the line being read moves
      // while it is read — and it makes "did recall eat what I was typing?"
      // answerable by accident. Tab above is the only path into the draft.
      //
      // Landing back on the draft rung ends the walk: the ladder returns
      // `stashedDraft`, which is the user's own text, and previewing that would
      // offer to insert what is already there.
      // The queue's LAST entry is the only queued rung — `core/compose/recall` says so,
      // and this must read the same end or Tab would take a different prompt
      // than the one previewed.
      const { items: queuedNow } = latest.current;
      previewQueuedId.current =
        move.state.position.kind === "queued"
          ? (queuedNow[queuedNow.length - 1]?.id ?? null)
          : null;
      setPreview(move.state.position.kind === "draft" ? null : move.text);
    },
    [input, setText, take, events],
  );

  return { onKeyDown, preview, reset };
}
