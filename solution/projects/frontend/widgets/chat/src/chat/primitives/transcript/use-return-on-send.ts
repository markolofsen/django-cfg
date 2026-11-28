/**
 * Sending returns the reader to the bottom.
 *
 * The React binding only; the decision is `core/screen`'s `isOwnSend`, tested
 * without a DOM. What is here is the one thing that cannot be pure — remembering
 * the previous list across renders.
 */

import { useEffect, useRef } from "react";

import { isOwnSend } from "../../core/screen";
import { useChatStore } from "../../store";

export function useReturnOnSend(ids: readonly string[], scrollToBottom: () => void): void {
  const store = useChatStore();
  // A ref, not state: nothing renders from it, and it must be read and written
  // inside the same effect pass.
  const seen = useRef<readonly string[] | null>(null);

  useEffect(() => {
    const previous = seen.current;
    seen.current = ids;
    // Read through the store rather than from a prop: the roles live beside the
    // ids in one state, so passing them in would let a caller hand over a list
    // and a role map that disagree.
    const roleOf = (id: string) => store.getState().transcript.byId[id]?.role;
    if (isOwnSend(previous, ids, roleOf)) scrollToBottom();
  }, [ids, store, scrollToBottom]);
}
