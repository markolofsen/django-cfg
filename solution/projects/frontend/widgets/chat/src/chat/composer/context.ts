/**
 * The composer's own context, deliberately separate from `ChatContext`.
 *
 * `useDraft()` holds per-composer state (the text being typed, the chips not yet
 * sent). Putting it on the chat context would make two composers on one screen
 * share a draft, and would re-render every transcript row on each keystroke —
 * the chat context is read by rows that must not care about typing.
 */

import { createContext, useContext } from "react";

import type { DraftApi } from "../store/composing/use-draft";

export const ComposerContext = createContext<DraftApi | null>(null);

export function useComposer(): DraftApi {
  const value = useContext(ComposerContext);
  if (value === null) {
    throw new Error("composer parts must be used inside <Composer>");
  }
  return value;
}

/**
 * The draft when there is one, null otherwise.
 *
 * For a part that must decide whether to render at all BEFORE it needs the
 * draft: hooks cannot run conditionally, so the throwing variant would fire
 * before an absent capability could return null.
 */
export function useOptionalComposer(): DraftApi | null {
  return useContext(ComposerContext);
}
