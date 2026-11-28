import { useCallback } from "react";

import { needsChoice } from "../../core/compose/text-replace";
import { useChatSurfaces } from "../../store";
import { useComposer } from "../context";

/**
 * Asked when the field already holds something the write would destroy.
 *
 * Injected like `confirmSendNow`: a dialog imported here would give the package
 * a dialog implementation and leave a second host no way to replace it.
 *
 * `true` ⇒ replace. A "no" costs nothing: the caller holds its own side of the
 * move until this resolves, so declining leaves the field AND the source as
 * they were.
 */
export type AskReplace = (incoming: string) => Promise<boolean>;

/**
 * Write text into the composer without silently destroying a draft.
 *
 * Resolves to whether the write happened, so a caller that also MOVES something
 * — taking a queued prompt out of the queue — can hold its own side until the
 * answer is in. The other order loses the prompt when the user cancels.
 *
 * Absent `ask` ⇒ replace outright. That is the honest default for a host with no
 * dialog; refusing the write instead would read as a dead control.
 */
export function useReplaceText(ask?: AskReplace): (incoming: string) => Promise<boolean> {
  const { draft, setText } = useComposer();
  // The registry already knows which form is this chat's composer, and already
  // retries on the next frame when it has not mounted. Locating the field here
  // instead would be a second answer to the same question — the failure
  // `surfaces.ts` was written to end.
  const surfaces = useChatSurfaces();

  return useCallback(
    async (incoming: string) => {
      if (incoming === "") return false;

      const write = (text: string) => {
        setText(text);
        // Deferred: React writes the value on the next commit, so focusing now
        // would put the caret against the OLD text and leave it mid-string.
        queueMicrotask(() => surfaces?.focusComposer());
      };

      if (!needsChoice(draft.text, incoming) || ask === undefined) {
        write(incoming);
        return true;
      }
      if (!(await ask(incoming))) return false;
      write(incoming);
      return true;
    },
    [draft.text, setText, surfaces, ask],
  );
}
