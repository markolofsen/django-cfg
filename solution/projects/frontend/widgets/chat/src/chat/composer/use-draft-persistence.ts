import { useEffect, useRef } from "react";

import { draftStorageKey, draftWrite, mayPersist, restoredDraft } from "../core/compose/draft-storage";
import { useComposer } from "./context";

/**
 * Keep an unsent draft across a reload, per room.
 *
 * `sessionStorage`, not `localStorage`: a draft should survive an accidental
 * reload, and should NOT still be waiting tomorrow in a room the user has left.
 * Prompt recall makes the opposite trade, hence the different store.
 *
 * TEXT ONLY — a staged file is an object-URL pinned to this document, so a
 * restored one is a chip that renders and cannot send. The ROOM is the
 * caller's; this package has no notion of one (`use-reload-on-revision.ts`
 * draws the same line).
 *
 * The rules live in `core/compose/draft-storage.ts` so they can be tested without a
 * DOM; this owns only the effects and refs.
 */

function read(key: string): string | null {
  // Guarded: a sandboxed iframe and an SSR pass both THROW here rather than
  // returning null, and a composer that cannot mount is worse than one that
  // forgets.
  try {
    return globalThis.sessionStorage?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

function write(key: string, text: string): void {
  const decision = draftWrite(text);
  try {
    if ("remove" in decision) globalThis.sessionStorage?.removeItem(key);
    else globalThis.sessionStorage?.setItem(key, decision.value);
  } catch {
    // Quota, or storage denied. The draft still applies to this session; failing
    // the keystroke because it cannot be saved would be the worse outcome.
  }
}

/**
 * Restore on mount, save on change.
 *
 * Clearing after a send needs no branch of its own: `send` resets the draft to
 * `emptyDraft`, so the save path writes `""`, which removes the entry. Adding a
 * send-specific hook here would give one behaviour two triggers.
 *
 * `room` changing means a different conversation: the effect restores that
 * room's draft rather than carrying the current text into it.
 */
export function useDraftPersistence(room: string | undefined): void {
  const { draft, setText } = useComposer();
  // Which room's restore has completed. The save effect stays inert until it
  // matches, so a restore is never overwritten by the emptiness preceding it.
  const restored = useRef<string | null>(null);
  // Read through a ref: seeding the restore effect with `setText` would re-arm
  // it whenever the draft identity changes, re-restoring mid-typing.
  const setTextRef = useRef(setText);
  setTextRef.current = setText;

  useEffect(() => {
    // Absent room ⇒ the host wants no persistence. Guarded inside the effect,
    // never by skipping the hook: a conditional call changes hook order the
    // first time a host makes the room conditional.
    if (room === undefined) return;
    const stored = restoredDraft(read(draftStorageKey(room)));
    restored.current = room;
    if (stored !== null) setTextRef.current(stored);
  }, [room]);

  useEffect(() => {
    if (room === undefined) return;
    if (!mayPersist(restored.current, room)) return;
    write(draftStorageKey(room), draft.text);
  }, [room, draft.text]);
}
