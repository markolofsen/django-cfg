import type { Attachment, ChatMessage, MessagePart } from '../../../chat/core';

import type { StoredMessage } from '../../wire/stored';
import { storedTraceParts } from '../../wire/trace';

/**
 * A stored message as a widget message. A `running` or `cancelled` one reads as interrupted: the thread never shows a spinner without a stream behind it
 * (a running message is resolved by `reconcile`, which reseeds the thread when the server finishes it). Parts are kept whatever their `kind`: the host's
 * renderers draw the kinds they know, as for a live answer.
 */
export function fromStored(message: StoredMessage, failedText: string): ChatMessage {
  // What the answer did comes first, as it did live (steps, then the words that followed).
  const parts: MessagePart[] = storedTraceParts(message.id, message.trace);
  if (message.text) parts.push({ id: `${message.id}:t`, type: 'text', text: message.text });
  for (const file of message.attachments ?? []) {
    const attachment: Attachment = { id: file.id, name: file.name, mime: file.mime, size: file.size, kind: file.kind as Attachment['kind'], url: file.url };
    parts.push({ id: `${message.id}:file:${file.id}`, type: 'attachment', attachment });
  }
  message.parts.forEach((part, index) => parts.push({ id: `${message.id}:w${index}`, type: 'data', kind: part.kind, data: part.data }));
  const status: ChatMessage['status'] =
    message.status === 'done' ? { state: 'complete' } : message.status === 'error' ? { state: 'failed', message: failedText } : { state: 'interrupted' };
  return { id: message.id, role: message.role, parts, status, createdAt: Date.parse(message.created_at) || 0 };
}

/** A hidden feedback turn is stored as a user row with no words (`sendFeedback`): it has no bubble, so it is left out. */
export const fromStoredThread = (messages: readonly StoredMessage[], failedText: string): ChatMessage[] =>
  messages.filter((m) => !(m.role === 'user' && !m.text && m.parts.length === 0 && !m.attachments?.length)).map((m) => fromStored(m, failedText));
