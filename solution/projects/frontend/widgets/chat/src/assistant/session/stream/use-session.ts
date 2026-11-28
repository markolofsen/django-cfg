'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { BLOCK_KINDS, type ChatAdapter, type ChatMessage } from '../../../chat/core';

import { useAssistantCopy, type SessionNotice } from '../../../i18n/assistant';
import { sessionCopyFor } from './session-copy';

import type { ChatContext, Phase } from '../../wire/frames';
import type { StoredConversation, StoredThread } from '../../wire/stored';
import { ThreadNotFoundError, type ChatHttpError, type ChatTransport } from '../../wire/transport';
import { createStreamAdapter, sendFeedbackTurn, type AdapterDeps } from './adapter';
import { fromStoredThread } from './from-stored';
import { reconcile } from './reconcile';
import { NO_SESSION, restoreSession, type SessionStorage, type ThreadApi } from '../threads/sessions';

/** The kinds a live payload may have: the host's explicit list, else the keys of its renderers plus the package's own blocks, else no filter (`undefined`). */
export function payloadKindsOf({ payloadKinds, dataRenderers }: Pick<SessionDeps, 'payloadKinds' | 'dataRenderers'>): readonly string[] | undefined {
  if (payloadKinds) return payloadKinds;
  return dataRenderers ? [...Object.keys(dataRenderers), ...BLOCK_KINDS] : undefined;
}

export interface SessionCopy {
  messages: AdapterDeps['messages'];
  /** Live label per phase ("Searching the catalog..."). */
  status: Record<Phase, string>;
  /** Shown on a message that ended in an error when the thread is reloaded. */
  failedText: string;
}

export interface SessionDeps {
  transport: ChatTransport;
  /** Absent: an anonymous session. Nothing is fetched or listed, the room starts empty, "new chat" empties it, and a lost stream cannot be reconciled (the notice offers Retry). */
  api?: ThreadApi;
  /** Remembers the last used session so a reload returns to it. Absent: the newest session is shown. */
  storage?: SessionStorage;
  getContext: () => ChatContext | undefined;
  /** The `kind`s the host draws; any other live payload is dropped and reported. Absent: the keys of `dataRenderers` plus the kinds the package draws itself (`ask`, `approval`, `changes`); with neither, every kind is forwarded. */
  payloadKinds?: readonly string[];
  /** The same map the host gives `AssistantChat`; only its keys are read, so a host lists its kinds once. `payloadKinds`, when given, wins. */
  dataRenderers?: Readonly<Record<string, unknown>>;
  onUnknownPayload?: (kind: string) => void;
  /** Absent: the bundled words for the active language. */
  copy?: SessionCopy;
  onRejected?: (error: ChatHttpError) => void;
  onNetworkFailure?: () => void;
}

/** `id` is the transcript's identity (the session plus a revision: a new one reseeds the widget); `session` is the session itself, `null` before the first send. */
export type ThreadState = { kind: 'loading' } | { kind: 'error' } | { kind: 'ready'; id: string; session: string | null; history: ChatMessage[] };

/** `reconnecting`: the stream was lost and the server is being asked; `stalled`: the answer is still running after the budget (offer Retry). */
export type { SessionNotice };

export interface Session {
  thread: ThreadState;
  adapter: ChatAdapter;
  /** Live progress label while a run streams; null otherwise. */
  statusLabel: string | null;
  notice: SessionNotice | null;
  /** Load the session again (after a load error or a stalled run). */
  reload: () => void;
  /** The viewer's sessions, newest activity first; `null` until `refreshSessions` has answered once. */
  sessions: StoredThread[] | null;
  refreshSessions: () => void;
  /** A turn is in flight: starting or switching a session waits for it (Stop ends it). */
  busy: boolean;
  /** "New chat": a new empty session, shown at once. A no-op while the current one is empty. Resolves `false` when it failed (nothing changed). */
  startNew: () => Promise<boolean>;
  /** Show another session. Resolves `false` when it failed (the current one stays). */
  switchTo: (id: string) => Promise<boolean>;
  /**
   * Tell the server what became of a card (`messageId` is the answer that carried it) as a hidden turn: empty text, `context.feedback = {message_id, payload}`,
   * no user bubble. The answer, if any, is shown by reloading the session from the server when the run ends. Rejects with the `ChatHttpError` of a refusal
   * (`code: 'already_given'` is the kind saying it already has this feedback) and with `ChatNetworkError`; resolves when the run ended.
   */
  sendFeedback: (messageId: string, payload: unknown) => Promise<void>;
}

/**
 * The signed-in assistant's sessions: the shown session from the server (no client copy), the adapter for new messages, the live status label, and the reconcile
 * that runs when a stream is lost. A new `history` identity (`id` carries a revision) reseeds the widget only between runs.
 */
export function useSession(given: SessionDeps): Session {
  const bundled = useAssistantCopy();
  const deps = { ...given, copy: given.copy ?? sessionCopyFor(bundled) };
  const ref = useRef(deps);
  ref.current = deps;
  const [thread, setThread] = useState<ThreadState>({ kind: 'loading' });
  const [phase, setPhase] = useState<Phase | null>(null);
  const [notice, setNotice] = useState<SessionNotice | null>(null);
  const [sessions, setSessions] = useState<StoredThread[] | null>(null);
  const [busy, setBusy] = useState(false);
  const revision = useRef(0);
  const live = useRef<AbortController | null>(null);
  /** The shown session's id; `null` before the first send. Written with the storage, in one place. */
  const current = useRef<string | null>(null);

  const remember = useCallback((id: string | null) => {
    current.current = id;
    ref.current.storage?.write(id);
  }, []);

  const seed = useCallback(
    (conversation: StoredConversation) => {
      revision.current += 1;
      remember(conversation.id);
      setThread({
        kind: 'ready',
        id: `${conversation.id ?? 'new'}:${revision.current}`,
        session: conversation.id,
        history: fromStoredThread(conversation.messages, ref.current.copy.failedText),
      });
    },
    [remember],
  );

  const load = useCallback(() => {
    live.current?.abort();
    const controller = new AbortController();
    live.current = controller;
    setThread({ kind: 'loading' });
    setNotice(null);
    const { api, storage } = ref.current;
    if (!api) return seed(NO_SESSION);
    const restore = () => restoreSession({ api, storage, signal: controller.signal });
    const read = current.current
      ? api.load(current.current, controller.signal).catch((error: unknown) => {
          if (!(error instanceof ThreadNotFoundError)) throw error;
          remember(null); // the shown session is gone: fall back to the newest
          return restore();
        })
      : restore();
    read.then(
      (conversation) => !controller.signal.aborted && seed(conversation),
      () => !controller.signal.aborted && setThread({ kind: 'error' }),
    );
  }, [seed, remember]);

  useEffect(() => {
    load();
    return () => live.current?.abort();
  }, [load]);

  // Derived from the renderers, so a new array per render: keyed by content, or the adapter would be rebuilt on every render.
  const wanted = payloadKindsOf(deps);
  const kindsKey = wanted?.join('\n');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const kinds = useMemo(() => wanted, [kindsKey]);
  const adapter = useMemo(
    () =>
      createStreamAdapter({
        transport: deps.transport,
        // The first send of a viewer with no session creates one; the shown transcript is not reseeded (that would drop the live message).
        threadFor: ref.current.api
          ? async () => {
              if (current.current) return current.current;
              const created = await ref.current.api!.create();
              remember(created.id);
              return created.id;
            }
          : undefined,
        getContext: () => ref.current.getContext(),
        onStatus: setPhase,
        payloadKinds: kinds,
        onUnknownPayload: (kind) => ref.current.onUnknownPayload?.(kind),
        onActive: setBusy,
        onRejected: (error) => {
          // The session vanished (purged, or another account's): forget it, the next send starts a fresh one.
          if (error.code === 'not_found') remember(null);
          ref.current.onRejected?.(error);
        },
        onNetworkFailure: () => ref.current.onNetworkFailure?.(),
        messages: {
          rejected: (error) => ref.current.copy.messages.rejected(error),
          streamError: (code, message) => ref.current.copy.messages.streamError(code, message),
          get failed() {
            return ref.current.copy.messages.failed;
          },
        },
        onInterrupted: () => {
          const api = ref.current.api;
          if (!api) return setNotice('stalled');
          setNotice('reconnecting');
          const controller = new AbortController();
          live.current = controller;
          reconcile({ fetchConversation: (signal) => api.load(current.current ?? '', signal), signal: controller.signal }).then(
            (result) => {
              if (controller.signal.aborted) return;
              if (result.outcome === 'timeout') return setNotice('stalled');
              setNotice(null);
              seed(result.conversation);
            },
            () => !controller.signal.aborted && setNotice('stalled'),
          );
        },
      }),
    // The transport is one per mounted chat; everything else is read through `ref`.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [deps.transport, kinds, Boolean(deps.api), seed, remember],
  );

  const refreshSessions = useCallback(() => {
    ref.current.api?.list(new AbortController().signal).then(setSessions, () => undefined);
  }, []);

  const show = useCallback(
    async (read: (signal: AbortSignal) => Promise<StoredConversation>): Promise<boolean> => {
      live.current?.abort();
      const controller = new AbortController();
      live.current = controller;
      try {
        const conversation = await read(controller.signal);
        if (controller.signal.aborted) return false;
        setNotice(null);
        seed(conversation);
        return true;
      } catch {
        return false;
      }
    },
    [seed],
  );

  const startNew = useCallback(async () => {
    if ((ref.current.api && current.current === null) || (thread.kind === 'ready' && thread.history.length === 0)) return true; // already a blank page
    const api = ref.current.api;
    if (!api) return show(async () => NO_SESSION);
    return show(async () => {
      const created = await api.create();
      return { id: created.id, messages: [] };
    });
  }, [show, thread]);

  const switchTo = useCallback(
    async (id: string) => (id === current.current || !ref.current.api ? true : show((signal) => ref.current.api!.load(id, signal))),
    [show],
  );

  const sendFeedback = useCallback(
    async (messageId: string, payload: unknown) => {
      const controller = new AbortController();
      live.current?.abort();
      live.current = controller;
      await sendFeedbackTurn(
        {
          transport: ref.current.transport,
          threadFor: ref.current.api
            ? async () => {
                if (current.current) return current.current;
                const created = await ref.current.api!.create();
                remember(created.id);
                return created.id;
              }
            : undefined,
          getContext: () => ref.current.getContext(),
          onStatus: setPhase,
          onActive: setBusy,
          onRejected: (error) => {
            if (error.code === 'not_found') remember(null);
            ref.current.onRejected?.(error);
          },
          onNetworkFailure: () => ref.current.onNetworkFailure?.(),
        },
        messageId,
        payload,
        controller.signal,
      );
      const api = ref.current.api;
      if (!api || controller.signal.aborted || !current.current) return;
      const conversation = await api.load(current.current, controller.signal).catch(() => null);
      if (conversation && !controller.signal.aborted) seed(conversation);
    },
    [seed, remember],
  );

  return { thread, adapter, statusLabel: phase ? ref.current.copy.status[phase] : null, notice, reload: load, sessions, refreshSessions, busy, startNew, switchTo, sendFeedback };
}
