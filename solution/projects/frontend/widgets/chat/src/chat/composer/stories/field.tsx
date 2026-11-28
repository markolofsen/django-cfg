import { useEffect, useRef, useState, type KeyboardEvent } from "react";

import { useRecall } from "../../store";
import { ComposerInput } from "../field/input";
import { useComposer } from "../context";
import { useDraftPersistence } from "../use-draft-persistence";

/**
 * The composer's FIELD, for stories: the textarea and ↑/↓ recall over it.
 *
 * Separate from `harness.tsx` because the seam is real, not because a limit
 * forced it: everything here is the field assembly, and the harness above it is
 * the surrounding chrome.
 */

const field = "w-full resize-none bg-transparent text-foreground outline-none";

/**
 * The field wiring, assembled independently of the shipped assembly.
 *
 * `field/field.tsx` is the shipped join; this is a SECOND, minimal one — which
 * is the point. A contract exercised in exactly one place is a contract nobody
 * has tested against a different caller. If the pieces only fit one way, they
 * fail to fit here, visibly.
 */
export function Field({
  initialText,
  sendOnMount,
  history,
  draftRoom,
}: {
  readonly initialText?: string;
  readonly sendOnMount: boolean;
  readonly history?: readonly string[];
  /** Persist the draft under this room. Absent ⇒ no persistence, as in a host. */
  readonly draftRoom?: string;
}) {
  const { draft, setText, send } = useComposer();
  const ref = useRef<HTMLTextAreaElement>(null);

  // The ladder GROWS as prompts are sent, because a fixed fixture would show
  // recall working over data no user action produced — and the interesting bug
  // (a sent prompt not reaching the ladder) would be invisible.
  const [sentPrompts, setSentPrompts] = useState<readonly string[]>(history ?? []);
  const recall = useRecall({ entries: sentPrompts, input: ref, draft, setText });

  // BEFORE the seed: effects run in call order, so a restore lands first and an
  // explicit `initialText` overrides it. To SEE a restore, pass no seed.
  useDraftPersistence(draftRoom);
  useSeed(initialText, setText);
  // AFTER the seed has reached the store, never beside it: `useSeed` writes
  // during render, so a send issued in the same pass would post an empty draft
  // and the story would park on an idle Send having proved nothing.
  useSendOnce(sendOnMount && draft.text.length > 0, send);

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // Record the prompt on Enter, BEFORE the composer clears the draft — after
    // it there is nothing left to record. A real host derives this from the
    // transcript (`core/compose/recall/from-transcript.ts`); a story has none.
    if (event.key === "Enter" && !event.shiftKey && draft.text.trim() !== "") {
      const text = draft.text;
      setSentPrompts((prev) => [...prev, text]);
      recall.reset();
    }
    recall.onKeyDown(event);
  };

  return (
    <div className="relative grid gap-1">
      <ComposerInput
        label="Message"
        placeholder="Ask anything…"
        className={field}
        ref={ref}
        onKeyDown={onKeyDown}
      />
    </div>
  );
}

/**
 * Send exactly once, in an effect, when `ready` first becomes true.
 *
 * An effect rather than the render-phase shortcut `useSeed` uses: `send()`
 * starts a turn and writes to the store, which during render would be a state
 * update in another component's render pass. Seeding text is idempotent; posting
 * a turn is not.
 */
function useSendOnce(ready: boolean, send: () => void) {
  const done = useRef(false);
  useEffect(() => {
    if (!ready || done.current) return;
    done.current = true;
    send();
  }, [ready, send]);
}

/**
 * Seed the field once, in an effect.
 *
 * `setText` writes to the composer store, so doing it during render updated
 * `Composer` from inside `Field`'s render pass — React's
 * "Cannot update a component while rendering a different component".
 */
function useSeed(text: string | undefined, setText: (value: string) => void) {
  const done = useRef(false);
  useEffect(() => {
    if (done.current || text === undefined) return;
    done.current = true;
    setText(text);
  }, [text, setText]);
}
