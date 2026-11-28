'use client';

import { ChatComposer } from '../../../chat/ui';

import { ComposerBehaviour } from './composer-behaviour';
import { suggestionIcon } from './suggestion-icons';
import { useSentPrompts } from './use-sent-prompts';

interface Props {
  speech?: { value: string; onChange: (language: string) => void };
  draftRoom: string;
  focusWhen?: boolean;
  refocus?: boolean;
  /** The phone-sized composer (see `AssistantChat composer`). */
  compact?: boolean;
}

/** The widget's composer with its recall fed from the live transcript and our behaviour mounted inside. Must sit inside the chat. */
export function AssistantComposer({ speech, draftRoom, focusWhen, refocus, compact }: Props) {
  const history = useSentPrompts();
  return <ChatComposer history={history} speechLanguage={speech} draftRoom={draftRoom} stacked={!compact} compact={compact} suggestionIcon={suggestionIcon} toolbarEnd={<ComposerBehaviour focusWhen={focusWhen} refocus={refocus} />} />;
}
