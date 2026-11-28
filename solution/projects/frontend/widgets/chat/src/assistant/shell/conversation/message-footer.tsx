'use client';

import { Check, Copy } from 'lucide-react';
import type { ReactNode } from 'react';

import { MessageActions, MessageTime, useCopyAction } from '../../../chat/ui';
import { useChatCopy } from '../../../i18n';
import { useMessageIds, useTurn } from '../../../chat/store';
import { type ChatMessage } from '../../../chat/core';

/** The row under each message: copy, and the time it was sent (shown with the actions). (Retry and the rest are the host's inventory, added here when the backend can honour them.) */
export function MessageFooter({ message, children }: { message: ChatMessage; /** The host's own row under the default one (see `AssistantChat footer`). */ children?: ReactNode }) {
  const copy = useChatCopy().message;
  // Only the newest message keeps its actions in view; every other row shows them on hover or focus, so the transcript stays quiet.
  const ids = useMessageIds();
  const last = ids[ids.length - 1] === message.id;
  // While an answer is on its way the newest row is still unfinished: no copy, no time, nothing to act on yet. An assistant row with no text has none either.
  const { isStreaming } = useTurn();
  const empty = message.role !== 'user' && !message.parts.some((part) => part.type === 'text' && part.text.trim() !== '');
  const action = useCopyAction(message, {
    label: copy.copy,
    copiedLabel: copy.copied,
    icon: <Copy className="size-3.5" aria-hidden="true" />,
    copiedIcon: <Check className="size-3.5" aria-hidden="true" />,
    write: async (text) => {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch {
        return false;
      }
    },
  });
  // Another participant's line sits on the left like the assistant's.
  const mine = message.role === 'user' && message.from !== 'other';
  const row =
    (isStreaming && last) || empty ? null : (
      <div className={`flex items-center gap-2 ${mine ? 'justify-end' : 'justify-start'}`}>
        <MessageActions message={message} actions={action ? [action] : []} className={last ? 'opacity-100' : 'opacity-0'} />
        <MessageTime message={message} className={last ? 'opacity-100' : undefined} />
      </div>
    );
  if (!children) return row;
  return (
    <div className="flex flex-col gap-1">
      {row}
      {children}
    </div>
  );
}
