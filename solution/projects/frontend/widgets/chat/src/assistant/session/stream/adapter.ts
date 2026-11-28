import type { ChatAdapter, StreamChunk } from '../../../chat/core';

import { stepPart } from '../../wire/trace';
import type { ChatContext, Frame, Phase, StreamErrorCode } from '../../wire/frames';
import { StreamLostError } from '../../wire/parse-sse';
import { ChatHttpError, ChatNetworkError, type ChatTransport } from '../../wire/transport';

export interface AdapterDeps {
  transport: ChatTransport;
  /** The session this message goes to: the current one, or a new one created now (the first send of a user who has none). A rejection ends the turn as a failed message. Absent: no session (an anonymous host). */
  threadFor?: () => Promise<string>;
  /** Scope of this turn, read at send time (the page the user is on). */
  getContext: () => ChatContext | undefined;
  /** Ephemeral progress for the live label above the composer; `null` when the run ends. Never enters the transcript. */
  onStatus: (phase: Phase | null) => void;
  /** A refusal before any frame (401, 409, 422, 429, 503): the host reacts (invitation, countdown, hide the entry point). */
  onRejected?: (error: ChatHttpError) => void;
  /** The `kind`s the host draws. A live `ui_payload` of another kind is dropped and reported to `onUnknownPayload`. Absent: every kind is forwarded. */
  payloadKinds?: readonly string[];
  onUnknownPayload?: (kind: string) => void;
  /** The stream ended without a terminal frame: the host reconciles from the server. */
  onInterrupted?: () => void;
  /** A turn is in flight (true at the send, false when its stream ends): the host holds session switching meanwhile. */
  onActive?: (active: boolean) => void;
  /** A network-level failure, for the connectivity monitor. */
  onNetworkFailure?: () => void;
  /** One plain sentence per outcome (the catalogue). */
  messages: {
    rejected: (error: ChatHttpError) => string;
    streamError: (code: StreamErrorCode, serverMessage: string) => string;
    failed: string;
  };
  newId?: () => string;
  /** Token coalescing window; `0` forwards every delta at once (tests). About 30 fps by default. */
  coalesceMs?: number;
}

const defaultId = () => globalThis.crypto.randomUUID();

/**
 * A hidden "system feedback" turn: posts empty text with `context.feedback = {message_id, payload}` and drains the run. No user bubble is added and nothing
 * enters the live transcript (the answer is stored on the server; the host reseeds from it). Resolves when the run ends; a refusal before any frame
 * (409 `already_given`, 409 `busy`, 429 ...) reaches `onRejected` and is thrown as the `ChatHttpError`, so the caller can branch on `error.code`.
 */
export async function sendFeedbackTurn(
  deps: Pick<AdapterDeps, 'transport' | 'threadFor' | 'getContext' | 'onStatus' | 'onRejected' | 'onActive' | 'onNetworkFailure' | 'newId'>,
  messageId: string,
  payload: unknown,
  signal: AbortSignal,
): Promise<void> {
  const clientId = (deps.newId ?? defaultId)();
  deps.onActive?.(true);
  try {
    const threadId = deps.threadFor ? await deps.threadFor() : undefined;
    const context = { ...deps.getContext(), feedback: { message_id: messageId, payload } };
    for await (const frame of deps.transport.open({ threadId, text: '', clientId, context, signal })) {
      if (frame.type === 'status') deps.onStatus(frame.phase);
      if (frame.type === 'done' || frame.type === 'error') break;
    }
  } catch (error) {
    if (error instanceof ChatHttpError) deps.onRejected?.(error);
    else if (error instanceof ChatNetworkError) deps.onNetworkFailure?.();
    throw error;
  } finally {
    deps.onStatus(null);
    deps.onActive?.(false);
  }
}

/**
 * The wire to the widget. Maps one run's frames to chunks (`run` opens the assistant message, `text_delta` grows its text, the optional `reasoning_delta` / `reasoning_end` frames drive the widget's own Reasoning part, `ui_payload` adds a card part after the text
 * it follows, `done` finishes, `error` fails keeping the partial text); a stream that ends without a terminal frame is `interrupted`, and the host reconciles from the server.
 * Everything a run needs travels inside its own ordered chunk stream: no shared buffer between runs.
 */
export function createStreamAdapter(deps: AdapterDeps): ChatAdapter {
  const newId = deps.newId ?? defaultId;
  const coalesceMs = deps.coalesceMs ?? 33;
  /** The last attempt that never reached `run`: resending the same text reuses its `client_id` (nothing ran, so the resend is idempotent). */
  let unsent: { text: string; clientId: string } | null = null;

  return {
    async sendMessage({ text, attachments, model, signal }) {
      const clientId = unsent?.text === text ? unsent.clientId : newId();
      unsent = { text, clientId };

      return new ReadableStream<StreamChunk>({
        async start(controller) {
          let messageId = '';
          let textPart: string | null = null;
          /** The open reasoning part (optional `reasoning_delta` frames); sealed by `reasoning_end` or by the next part. */
          let thoughtPart: string | null = null;
          let parts = 0;
          /** Step ids already drawn: a step is sent twice (running, then settled) and the second frame updates the same part. */
          const steps = new Set<string>();
          let pending = '';
          /** The part `pending` belongs to, with the chunk that carries it. */
          let pendingKind: 'text-delta' | 'reasoning-delta' = 'text-delta';
          let timer: ReturnType<typeof setTimeout> | null = null;
          let terminal = false;
          deps.onActive?.(true);

          const open = (id: string) => {
            messageId = id;
            controller.enqueue({ type: 'message-start', messageId: id, createdAt: Date.now() });
          };
          const flush = () => {
            if (timer) clearTimeout(timer);
            timer = null;
            const target = pendingKind === 'text-delta' ? textPart : thoughtPart;
            if (pending && target) controller.enqueue({ type: pendingKind, partId: target, delta: pending });
            pending = '';
          };
          const queue = (kind: 'text-delta' | 'reasoning-delta', delta: string) => {
            if (pending && pendingKind !== kind) flush();
            pendingKind = kind;
            pending += delta;
            if (coalesceMs === 0) flush();
            else timer ??= setTimeout(flush, coalesceMs);
          };
          const endThought = (elapsedMs?: number, tokens?: number) => {
            if (!thoughtPart) return;
            flush();
            controller.enqueue({ type: 'reasoning-end', partId: thoughtPart, ...(elapsedMs === undefined ? {} : { elapsedMs }), ...(tokens === undefined ? {} : { tokens }) });
            thoughtPart = null;
          };
          const fail = (message: string) => {
            endThought();
            flush();
            if (!messageId) open(`local-${clientId}`);
            controller.enqueue({ type: 'error', message });
            terminal = true;
          };
          const handle = (frame: Frame) => {
            switch (frame.type) {
              case 'run':
                unsent = null;
                open(frame.message_id);
                break;
              case 'status':
                deps.onStatus(frame.phase);
                break;
              case 'text_delta':
                if (!messageId) break;
                endThought();
                if (!textPart) {
                  textPart = `${messageId}:t${parts++}`;
                  controller.enqueue({ type: 'text-start', partId: textPart });
                }
                queue('text-delta', frame.delta);
                break;
              case 'reasoning_delta':
                if (!messageId) break;
                if (!thoughtPart) {
                  flush();
                  textPart = null;
                  thoughtPart = `${messageId}:r${parts++}`;
                  controller.enqueue({ type: 'reasoning-start', partId: thoughtPart });
                }
                queue('reasoning-delta', frame.delta);
                break;
              case 'reasoning_end':
                endThought(frame.elapsed_ms ?? undefined, frame.tokens ?? undefined);
                break;
              case 'trace_step': {
                if (!messageId) break;
                if (!steps.has(frame.step.stepId)) {
                  // A new step ends the open thought and the open text: whatever follows is a new part after it.
                  steps.add(frame.step.stepId);
                  endThought();
                  flush();
                  textPart = null;
                }
                controller.enqueue({ type: 'step', part: stepPart(messageId, frame.step) });
                break;
              }
              case 'ui_payload':
                if (!messageId) break;
                if (deps.payloadKinds && !deps.payloadKinds.includes(frame.kind)) {
                  deps.onUnknownPayload?.(frame.kind);
                  break;
                }
                endThought();
                flush();
                textPart = null;
                controller.enqueue({ type: 'data', part: { type: 'data', id: `${messageId}:w${parts++}`, kind: frame.kind, data: frame.data } });
                break;
              case 'done':
                endThought();
                flush();
                controller.enqueue({ type: 'finish' });
                terminal = true;
                break;
              case 'error':
                fail(deps.messages.streamError(frame.code, frame.message));
                break;
            }
          };

          try {
            const threadId = deps.threadFor ? await deps.threadFor() : undefined;
            for await (const frame of deps.transport.open({ threadId, text, clientId, context: deps.getContext(), ...(attachments.length === 0 ? {} : { attachments }), ...(model === undefined ? {} : { model }), signal })) {
              handle(frame);
              if (terminal) break;
            }
            if (!terminal) {
              endThought();
              flush();
              if (!signal.aborted) {
                controller.enqueue({ type: 'interrupted' });
                deps.onInterrupted?.();
              }
            }
          } catch (error) {
            if (error instanceof ChatHttpError) {
              deps.onRejected?.(error);
              fail(deps.messages.rejected(error));
            } else if (error instanceof ChatNetworkError) {
              deps.onNetworkFailure?.();
              fail(deps.messages.failed);
            } else if (error instanceof StreamLostError) {
              endThought();
              flush();
              controller.enqueue({ type: 'interrupted' });
              deps.onInterrupted?.();
            } else {
              fail(deps.messages.failed);
            }
          } finally {
            if (timer) clearTimeout(timer);
            deps.onStatus(null);
            deps.onActive?.(false);
            controller.close();
          }
        },
      });
    },
  };
}
