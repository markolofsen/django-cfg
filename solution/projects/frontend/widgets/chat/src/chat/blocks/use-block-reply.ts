import { useCallback, useSyncExternalStore } from "react";

import { useChatStore } from "../store/hooks";

export interface BlockReply {
  /** Send `text` as the user's next message. */
  readonly reply: (text: string) => void;
  /** A later user message exists, so this block is history: it must not ask again (a reloaded transcript shows it settled). */
  readonly settled: boolean;
}

/**
 * How a block answers: as an ordinary user message, through the same store the composer sends through, so the agent reads the answer in its next turn and no new wire shape exists.
 * `settled` is read from the transcript, which is what keeps a block that was answered in another session, or before a reload, from offering its buttons again.
 */
export function useBlockReply(messageId: string): BlockReply {
  const store = useChatStore();
  const snapshot = useCallback(() => {
    const { ids, byId } = store.getState().transcript;
    const at = ids.indexOf(messageId);
    return at >= 0 && ids.slice(at + 1).some((id) => byId[id]?.role === "user");
  }, [store, messageId]);
  // The same read on the server: a transcript that is already there must render settled in the first markup, or hydration disagrees with it.
  const settled = useSyncExternalStore(store.subscribe, snapshot, snapshot);
  const reply = useCallback((text: string) => void store.send({ text }), [store]);
  return { reply, settled };
}
