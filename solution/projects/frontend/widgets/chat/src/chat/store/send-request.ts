import type { SendRequest } from "../core/conversation/adapter";
import type { ChatMessage } from "../core/conversation/parts";
import type { Draft } from "../core/compose/outbound";
import { defaultRecipient } from "../core/room/recipient";

/** What the adapter is asked for one turn: the outbound text, the prior turns, and who the line is for. `messageId` is the optimistic message's id, so a host can reuse it as a client id. */
export function sendRequest(
  draft: Draft,
  messageId: string,
  text: string,
  history: readonly ChatMessage[],
  signal: AbortSignal,
): SendRequest {
  return {
    text,
    history,
    ...(draft.replyTo ? { replyTo: draft.replyTo } : {}),
    recipient: draft.to ?? defaultRecipient,
    mentions: draft.mentions ?? [],
    messageId,
    attachments: draft.attachments ?? [],
    signal,
  };
}

/** The request with the chosen model id on it, or unchanged when the host offers no choice. */
export function withModel(request: SendRequest, model: string | undefined): SendRequest {
  return model === undefined ? request : { ...request, model };
}

/** Sentinel for "the signal won the race", distinguishable from a read result. */
export const ABORTED = Symbol("aborted");

export function aborted(signal: AbortSignal): Promise<typeof ABORTED> {
  if (signal.aborted) return Promise.resolve(ABORTED);
  return new Promise((resolve) => {
    signal.addEventListener("abort", () => resolve(ABORTED), { once: true });
  });
}
