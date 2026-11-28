import { useMemo } from 'react';

import { isTextPart } from '../../../chat/core';
import { useChatStore, useMessageIds } from '../../../chat/store';

/**
 * The prompts sent in this room, oldest first, for the arrow-key recall: read from the LIVE transcript, so a question sent a moment ago is the first one recalled.
 * (A list taken from the history the room was seeded with only changes on a reload, and recall then walked to an old question instead of the latest.)
 */
export function useSentPrompts(): string[] {
  const store = useChatStore();
  const ids = useMessageIds();
  return useMemo(() => {
    const { byId } = store.getState().transcript;
    return ids
      .map((id) => byId[id])
      .filter((message) => message?.role === 'user')
      .map((message) => message!.parts.filter(isTextPart).map((part) => part.text).join('').trim())
      .filter(Boolean);
  }, [store, ids]);
}
